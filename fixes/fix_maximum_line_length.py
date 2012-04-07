from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Leaf, LParen, RParen, find_indentation, parenthesize
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols
from textwrap import TextWrapper

from .utils import tuplize_comments

MAX_CHARS = 79

def get_quotes(text):
    # Returns the quote type start and end
    # TODO clean this up for additional String literal types
    
    if text[:4] == u'u"""' or text[:4] == u"u'''":
        quote_start = text[:4]
    else:
        # TODO this needs to be cleaned up to deal with non-unicode strings
        quote_start = text[:2]
    if quote_start[0] not in [u'"', u"'"]:
        # Starts with a 'u' or something like that
        return (quote_start, quote_start[1:])
    else:
        return (quote_start, quote_start)


class FixMaximumLineLength(BaseFix):
    u''' No line should be greater than 80 characters.
    
    TODO: unicode chars have different length
    TODO: project wide search for string concat
    TODO: docstrings can start with #s
    '''
    
    def match(self, node):
        if node.type == token.NEWLINE or node.type == token.COLON:
            if node.column > MAX_CHARS:
                return True
        elif any(len(line) > MAX_CHARS for line in node.prefix.split('\n')):
            # There is a line in the prefix greater than MAX_CHARS
            return True
        return False
    
    def transform(self, node, results):
        if any(len(line) > MAX_CHARS for line in node.prefix.split(u'\n')):
            # Needs to fix the prefix
            
            trailing_spaces = len(node.prefix) - len(node.prefix.rstrip(u' '))
            
            before_comments, comments, after_comments = tuplize_comments(node.prefix)
            comment_indent_level = comments.index(u'#')
            
            # Combine all comment lines together
            all_comments = u' '.join([line.replace(u'#', '').lstrip() for line in comments.split(u'\n')])
            comment_prefix = u'%s# ' % (u' ' * comment_indent_level)
            
            wrapper = TextWrapper(width=MAX_CHARS, initial_indent=comment_prefix, subsequent_indent=comment_prefix)
            split_lines = wrapper.wrap(all_comments)

            new_prefix = u'%s%s\n%s' % (before_comments, u'\n'.join(split_lines), u' ' * trailing_spaces)  # Append the trailing spaces back
            node.prefix = new_prefix
            node.changed()
        else:
            # Need to fix the node itself
            
            node_to_split = node.prev_sibling
            if not node_to_split:
                return
            if node_to_split.type == token.STRING:
                # docstrings
                quote_start, quote_end = get_quotes(node_to_split.value)
                max_length = MAX_CHARS - node_to_split.column - len(quote_start)
            
                triple_quoted = quote_start.count(u'"""') or quote_start.count(u"'''")
            
                if triple_quoted:
                    wrapper = TextWrapper(width=max_length, subsequent_indent=u' ' * (4 + node_to_split.column))
                    split_lines = wrapper.wrap(node_to_split.value)
                    first_line = split_lines.pop(0)
                
                    new_nodes = [Leaf(token.STRING, first_line)]
                    for line in split_lines:
                        new_nodes.extend([Leaf(token.NEWLINE, u'\n'), Leaf(token.STRING, line)])
                    #new_nodes[-1].value = u"%s%s" % (new_nodes[-1].value, quote_end)
                else:
                    wrapper = TextWrapper(width=max_length, subsequent_indent=u'%s%s' % (u' ' * (4 + node_to_split.column), quote_start))
                    split_lines = wrapper.wrap(node_to_split.value)
                    first_line = split_lines.pop(0)
                
                    # If it's not triple quoted, we need to paren it
                    first_line = u"(%s" % first_line
                    split_lines[-1] = u"%s)" % split_lines[-1]
                    new_nodes = [Leaf(token.STRING, u"%s%s" % (first_line, quote_end))]
                    for line in split_lines:
                        new_nodes.extend([Leaf(token.NEWLINE, u'\n'), Leaf(token.STRING, line)])
            
                node_to_split.replace(new_nodes)
                node_to_split.changed()
            else:
                child_leaves = []
                # The first leaf after the limit
                first_leaf_gt_limit = None
                for leaf in node_to_split.leaves():
                    if leaf.column < MAX_CHARS:
                        first_leaf_gt_limit = leaf
                    child_leaves.append(leaf)

                # Since this node will be at the beginning of the line, strip the prefix
                first_leaf_gt_limit.prefix = first_leaf_gt_limit.prefix.strip()

                # We need to note if we are breaking on a func call, because that will mandate parens latet
                breaking_on_func_call = False
                if first_leaf_gt_limit.prev_sibling == Leaf(token.DOT, u'.'):
                    breaking_on_func_call = True
            
                parent_depth = find_indentation(node_to_split)
                new_indent = u"%s%s" % (u' ' * 4,  parent_depth)  # For now, just indent additional lines by 4 more spaces
                first_leaf_gt_limit.replace([Leaf(token.NEWLINE, u'\n'), Leaf(token.INDENT, new_indent), first_leaf_gt_limit])
                first_leaf_gt_limit.changed()

                # Parenthesize the parent since we inserted newlines between leaves above
                if node_to_split.type == python_symbols.print_stmt:
                    # print "hello there"
                    if node_to_split.children[1] != LParen():
                        # node_to_split.children[0] is the "print" literal
                        # strip the current 1st child, since we will be prepending an LParen
                        node_to_split.children[1].prefix = node_to_split.children[1].prefix.strip()
                        node_to_split.children[1].changed()
                        node_to_split.insert_child(1, LParen())
                        node_to_split.append_child(RParen())
                        node_to_split.changed()
                elif node_to_split.type == python_symbols.expr_stmt:
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
                elif node_to_split.type == python_symbols.power or node_to_split.type == python_symbols.atom:
                    # a.b().c()
                
                    # We don't need to add parens if we are calling a func and not splitting on a func call
                    if node_to_split.type == python_symbols.power and not breaking_on_func_call:
                        pass
                    elif node_to_split.children[0] != LParen():
                        node_to_split.insert_child(0, LParen())
                        node_to_split.append_child(RParen())
                        node_to_split.changed()
                elif node_to_split.type == python_symbols.parameters:
                    # Paramteres are always parenthesized already
                    pass
                else:
                    pass
                    #import pdb;pdb.set_trace()