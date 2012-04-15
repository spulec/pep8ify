from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Leaf, LParen, RParen, find_indentation
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as symbols
from textwrap import TextWrapper

from .utils import tuplize_comments, get_quotes

MAX_CHARS = 79


class FixMaximumLineLength(BaseFix):
    u'''
    Limit all lines to a maximum of 79 characters.

    There are still many devices around that are limited to 80 character
    lines; plus, limiting windows to 80 characters makes it possible to have
    several windows side-by-side.  The default wrapping on such devices looks
    ugly.  Therefore, please limit all lines to a maximum of 79 characters.
    For flowing long blocks of text (docstrings or comments), limiting the
    length to 72 characters is recommended.
    '''
    
    def match(self, node):
        if node.type in [token.NEWLINE, token.COLON]:
            # Sometimes the newline is wrapped into the next node, so we need to check the colons also.
            if node.column > MAX_CHARS:
                return True
        elif any(len(line) > MAX_CHARS for line in node.prefix.split('\n')):
            # There is a line in the prefix greater than MAX_CHARS
            return True
        return False
    
    def transform(self, node, results):
        if any(len(line) > MAX_CHARS for line in node.prefix.split(u'\n')):
            # Need to fix the prefix
            self.fix_prefix(node)
        else:
            node_to_split = node.prev_sibling
            if not node_to_split:
                return
            if node_to_split.type == token.STRING:
                self.fix_docstring(node_to_split)
            else:
                self.fix_leaves(node_to_split)

    def fix_prefix(self, node):
        before_comments, comments, after_comments = tuplize_comments(node.prefix)

        # Combine all comment lines together
        all_comments = u' '.join([line.replace(u'#', '', 1).lstrip() for line in comments.split(u'\n')])

        comment_indent_level = comments.index(u'#')
        comment_prefix = u'%s# ' % (u' ' * comment_indent_level)

        wrapper = TextWrapper(width=MAX_CHARS, initial_indent=comment_prefix, subsequent_indent=comment_prefix)
        split_lines = wrapper.wrap(all_comments)

        #if node.prefix.count(u'\n'): import pdb;pdb.set_trace()
        # We need to add back a newline that was lost above
        # after_comments = u"\n%s" % after_comments

        node.prefix = u'%s%s\n%s' % (before_comments, u'\n'.join(split_lines), after_comments)  # Append the trailing spaces back
        node.changed()

    def fix_docstring(self, node_to_split):
        # docstrings
        quote_start, quote_end = get_quotes(node_to_split.value)
        max_length = MAX_CHARS - node_to_split.column

        triple_quoted = quote_start.count(u'"""') or quote_start.count(u"'''")
        comment_indent = u' ' * (4 + node_to_split.column)

        if not triple_quoted:
            # If it's not tripled-quoted, we need to start and end each line with quotes
            comment_indent = u'%s%s' % (comment_indent, quote_start)
            # Since we will be appending the end_quote after each line after the splitting
            max_length -= len(quote_end)
            # If it's not triple quoted, we need to paren it
            node_to_split.value = u"(%s)" % node_to_split.value

        wrapper = TextWrapper(width=max_length, subsequent_indent=comment_indent)
        split_lines = wrapper.wrap(node_to_split.value)

        if not triple_quoted:
            # If it's not triple quoted, we need to close each line except for the last one
            split_lines = [u"%s%s" % (line, quote_end) if index != len(split_lines) - 1 else line for index, line in enumerate(split_lines)]

        new_nodes = [Leaf(token.STRING, split_lines.pop(0))]
        for line in split_lines:
            new_nodes.extend([Leaf(token.NEWLINE, u'\n'), Leaf(token.STRING, line)])

        node_to_split.replace(new_nodes)
        node_to_split.changed()

    def fix_leaves(self, node_to_split):
        child_leaves = []
        # The first leaf after the limit
        first_leaf_gt_limit = None
        for leaf in node_to_split.leaves():
            if leaf.column < MAX_CHARS:
                first_leaf_gt_limit = leaf
            child_leaves.append(leaf)

        if first_leaf_gt_limit.was_changed:
            # It's possible this node was already fixed by another pass-through
            return

        # Since this node will be at the beginning of the line, strip the prefix
        first_leaf_gt_limit.prefix = first_leaf_gt_limit.prefix.strip()

        # We need to note if we are breaking on a func call, because that will mandate parens later
        breaking_on_func_call = False
        if first_leaf_gt_limit.prev_sibling == Leaf(token.DOT, u'.'):
            breaking_on_func_call = True

        parent_depth = find_indentation(node_to_split)
        new_indent = u"%s%s" % (u' ' * 4,  parent_depth)  # For now, just indent additional lines by 4 more spaces

        first_leaf_gt_limit.replace([Leaf(token.NEWLINE, u'\n'), Leaf(token.INDENT, new_indent), first_leaf_gt_limit])
        first_leaf_gt_limit.changed()

        # Parenthesize the parent since we inserted newlines between leaves
        self.parenthesize_parent(node_to_split, breaking_on_func_call)

    def parenthesize_parent(self, node_to_split, breaking_on_func_call):
        if node_to_split.type == symbols.print_stmt:
            self.parenthesize_print_stmt(node_to_split)
        elif node_to_split.type == symbols.expr_stmt:
            self.parenthesize_expr_stmt(node_to_split)
        elif node_to_split.type in [symbols.power, symbols.atom]:
            self.parenthesize_call_stmt(node_to_split, breaking_on_func_call)
        elif node_to_split.type == symbols.parameters:
            # Paramteres are always parenthesized already
            pass

    def parenthesize_print_stmt(self, node_to_split):
        # print "hello there"
        if node_to_split.children[1] != LParen():
            # node_to_split.children[0] is the "print" literal
            # strip the current 1st child, since we will be prepending an LParen
            node_to_split.children[1].prefix = node_to_split.children[1].prefix.strip()
            node_to_split.children[1].changed()
            node_to_split.insert_child(1, LParen())
            node_to_split.append_child(RParen())
            node_to_split.changed()

    def parenthesize_expr_stmt(self, node_to_split):
        # x = "%s%s" % ("foo", "bar")
        value_node = node_to_split.children[2]
        if value_node.children[0] != LParen():
            # strip the current 1st child and add a space, since we will be prepending an LParen
            value_node.children[0].prefix = value_node.children[0].prefix.strip()
            value_node.children[0].changed()
            
            # We set a space prefix since this is after the '='
            left_paren = LParen()
            left_paren.prefix = u" "
            value_node.insert_child(0, left_paren)
            value_node.append_child(RParen())
            value_node.changed()

    def parenthesize_call_stmt(self, node_to_split, breaking_on_func_call):
        # a.b().c()
        if node_to_split.type == symbols.power and not breaking_on_func_call:
            # We don't need to add parens if we are calling a func and not splitting on a func call
            pass
        elif node_to_split.children[0] != LParen():
            node_to_split.insert_child(0, LParen())
            node_to_split.append_child(RParen())
            node_to_split.changed()
