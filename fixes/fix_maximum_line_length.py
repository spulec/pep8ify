from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import LParen, RParen, find_indentation
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as symbols
from lib2to3.pytree import Leaf, Node
from textwrap import TextWrapper

from .utils import tuplize_comments, get_quotes, wrap_leaves

MAX_CHARS = 79
OPENING_TOKENS = [token.LPAR, token.LSQB, token.LBRACE]
CLOSING_TOKENS = [token.RPAR, token.RSQB, token.RBRACE]


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
        #if node.next_sibling and node.next_sibling.type in [token.NEWLINE, token.COLON]:
        if node.type in [token.NEWLINE, token.COLON]:
            # Sometimes the newline is wrapped into the next node, so we need to check the colons also.
            #if node.next_sibling.column > MAX_CHARS:
            if node.column > MAX_CHARS:
                return True
        if any(len(line) > MAX_CHARS for line in node.prefix.split('\n')):
            # There is a line in the prefix greater than MAX_CHARS
            return True
        return False
    
    def transform(self, node, results):
        # next_sibling = node.next_sibling
        # if next_sibling and (any(len(line) > MAX_CHARS for line in next_sibling.prefix.split(u'\n')) or
        #     (next_sibling.prefix.count(u"#") and next_sibling.column + len(next_sibling.prefix) > MAX_CHARS)):
        #     # Need to fix the prefix
        #     self.fix_prefix(next_sibling)
        if (any(len(line) > MAX_CHARS for line in node.prefix.split(u'\n')) or
            node.prefix.count(u"#") and node.column + len(node.prefix) > MAX_CHARS):
            # Need to fix the prefix
            self.fix_prefix(node)
        # if (node.next_sibling and node.next_sibling.type in [token.NEWLINE, token.COLON]
        #     and node.next_sibling.column - len(node.next_sibling.prefix) > MAX_CHARS):
        if node.type in [token.NEWLINE, token.COLON] and node.column - len(node.prefix) > MAX_CHARS:
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
        all_comments = u' '.join([line.replace(u'#', u'', 1).lstrip() for line in comments.split(u'\n')])

        # It's an inline comment if it has not newlines
        is_inline_comment = not node.prefix.count(u'\n')

        initial_indent_level = comments.index(u'#')
        if is_inline_comment:
            # If inline comment, find where the prev sibling started to know
            # how to indent lines
            initial_indent_level = node.prev_sibling.children[0].column
        indent = u'%s# ' % (u' ' * initial_indent_level)

        wrapper = TextWrapper(width=MAX_CHARS, initial_indent=indent, subsequent_indent=indent)
        split_lines = wrapper.wrap(all_comments)

        if is_inline_comment:
            # If inline comment is too long, we'll move it to the next line
            split_lines[0] = u"\n%s" % split_lines[0]
        else:
            #We need to add back a newline that was lost above
            after_comments = u"\n%s" % after_comments
        new_prefix = u'%s%s%s' % (before_comments, u'\n'.join(split_lines), after_comments)  # Append the trailing spaces back
        if node.prefix != new_prefix:
            node.prefix = new_prefix
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
        parent_depth = find_indentation(node_to_split)
        new_indent = u"%s%s" % (u' ' * 4,  parent_depth)  # For now, just indent additional lines by 4 more spaces
        
        child_leaves = []
        for index, leaf in enumerate(node_to_split.leaves()):
            # We want to strip all newlines so we can properly insert newlines where they should be
            if leaf.type != token.NEWLINE:
                if leaf.prefix.count(u'\n') and index:
                    # If the line contains a newline, we need to strip all whitespace since there were leading indent spaces
                    leaf.prefix = u" "
                child_leaves.append(leaf)
        
        # Like TextWrapper, but for nodes.
        # We split on MAX_CHARS - 1 since we may need to insert a leading parenth.
        # It's not great, but it would be hard to do properly.
        split_leaves = wrap_leaves(child_leaves, width=MAX_CHARS - 1, subsequent_indent=new_indent)
        new_node = Node(node_to_split.type, [])

        # We want to keep track of if we are breaking inside a parenth
        open_count = 0
        need_parens = False
        for line_index, curr_line_nodes in enumerate(split_leaves):
            for node_index, curr_line_node in enumerate(curr_line_nodes):
                if line_index and not node_index:
                    # If first node in non-first line, reset prefix since there may have been spaces previously
                    curr_line_node.prefix = new_indent
                new_node.append_child(curr_line_node)
                if curr_line_node.type in OPENING_TOKENS:
                    open_count += 1
                if curr_line_node.type in CLOSING_TOKENS:
                    open_count -= 1

            if line_index != len(split_leaves) - 1:
                # Don't add newline at the end since it it part of the next sibling
                new_node.append_child(Leaf(token.NEWLINE, u'\n'))

                # Checks if we ended a line without being surrounded by parens
                if open_count <= 0:
                    need_parens = True
        if need_parens:
            # Parenthesize the parent if we're not inside parenths, braces, brackets, since we inserted newlines between leaves
            self.parenthesize_parent(new_node)
        node_to_split.replace(new_node)

    def parenthesize_parent(self, node_to_split):
        if node_to_split.type in [symbols.print_stmt, symbols.return_stmt]:
            self.parenthesize_print_or_return_stmt(node_to_split)
        elif node_to_split.type == symbols.expr_stmt:
            self.parenthesize_expr_stmt(node_to_split)
        elif node_to_split.type in [symbols.power, symbols.atom]:
            self.parenthesize_call_stmt(node_to_split)
        elif node_to_split.type == symbols.import_from:
            self.parenthesize_import_stmt(node_to_split)
        elif node_to_split.type in [symbols.or_test, symbols.and_test, 
            symbols.not_test, symbols.test, symbols.arith_expr, symbols.comparison]:
            self.parenthesize_test(node_to_split)
        elif node_to_split.type == symbols.parameters:
            # Paramteres are always parenthesized already
            pass

    def parenthesize_test(self, node_to_split):
        first_child = node_to_split.children[0]
        if first_child != LParen():
            # node_to_split.children[0] is the "print" literal
            # strip the current 1st child, since we will be prepending an LParen
            if first_child.prefix != first_child.prefix.strip():
                first_child.prefix = first_child.prefix.strip()
                first_child.changed()
            node_to_split.insert_child(0, LParen())
            node_to_split.append_child(RParen())
            node_to_split.changed()

    def parenthesize_print_or_return_stmt(self, node_to_split):
        # print "hello there"
        # return a, b
        second_child = node_to_split.children[1]
        if second_child != LParen():
            # node_to_split.children[0] is the "print" literal
            # strip the current 1st child, since we will be prepending an LParen
            if second_child.prefix != second_child.prefix.strip():
                second_child.prefix = second_child.prefix.strip()
                second_child.changed()
            node_to_split.insert_child(1, LParen())
            node_to_split.append_child(RParen())
            node_to_split.changed()

    def parenthesize_import_stmt(self, node_to_split):
        # from x import foo, bar
        imports_index = 0
        # Get the index of the first imported item
        for index, child in enumerate(node_to_split.children):
            if child.value == "import":
                imports_index = index + 1
                break
        first_import_child = node_to_split.children[imports_index]
        if first_import_child != LParen():
            # strip the current 1st child, since we will be prepending an LParen
            if first_import_child.prefix != first_import_child.prefix.strip():
                first_import_child.prefix = first_import_child.prefix.strip()
                first_import_child.changed()
            # We set a space prefix since this is after the '='
            left_paren = LParen()
            left_paren.prefix = u" "
            node_to_split.insert_child(imports_index, left_paren)
            node_to_split.append_child(RParen())
            node_to_split.changed()

    def parenthesize_expr_stmt(self, node_to_split):
        # x = "%s%s" % ("foo", "bar")
        value_node = node_to_split.children[2]
        if value_node != LParen():
            # strip the current 1st child and add a space, since we will be prepending an LParen
            if value_node.prefix != value_node.prefix.strip():
                value_node.prefix = value_node.prefix.strip()
                value_node.changed()
            
            # We set a space prefix since this is after the '='
            left_paren = LParen()
            left_paren.prefix = u" "
            node_to_split.insert_child(2, left_paren)
            node_to_split.append_child(RParen())
            node_to_split.changed()

    def parenthesize_call_stmt(self, node_to_split):
        # a.b().c()
        first_child = node_to_split.children[0]
        if first_child != LParen():
            # Since this can be at the beginning of a line, we can't just
            # strip the prefix, we need to keep leading whitespace
            first_child.prefix = u"%s(" % first_child.prefix
            first_child.changed()
            node_to_split.append_child(RParen())
            node_to_split.changed()
