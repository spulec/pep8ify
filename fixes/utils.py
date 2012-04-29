from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as symbols

BINARY_OPERATORS = frozenset(['**=', '*=', '+=', '-=', '!=', '<>',
    '%=', '^=', '&=', '|=', '==', '/=', '//=', '<=', '>=', '<<=', '>>=',
    '%', '^', '&', '|', '=', '/', '//', '<', '>', '<<'])
UNARY_OPERATORS = frozenset(['>>', '**', '*', '+', '-'])
OPERATORS = BINARY_OPERATORS | UNARY_OPERATORS
MAX_CHARS = 79


def get_leaves_after_last_newline(node):
    # Get all of the leaves after the last newline leaf
    all_leaves = []
    for leaf in node.leaves():
        all_leaves.append(leaf)
    last_newline_leaf_index = -1
    for index, leaf in enumerate(all_leaves):
        if leaf.type == token.NEWLINE:
            last_newline_leaf_index = index
    return all_leaves[last_newline_leaf_index + 1:]


def get_whitespace_before_definition(node):
    if node.prev_sibling:
        return get_last_child_with_whitespace(node.prev_sibling)


def get_last_child_with_whitespace(node):
    leaves = []
    for leaf in node.leaves():
        leaves.append(leaf)
    reverse_leaves = reversed(leaves)
    for leaf in reverse_leaves:
        if u'\n' in leaf.prefix or leaf.value == u'\n':
            return leaf


def has_parent(node, symbol_type):
    # Returns if node has a parent of type symbol_type
    if node.parent:
        return node.parent.type == symbol_type or has_parent(node.parent,
            symbol_type)


def prefix_indent_count(node):
    # Find the number of spaces preceding this line
    return len(node.prefix.split(u'\n')[-1].replace(u'\t', u' ' * 4))


def tuplize_comments(prefix):
    # This tuplizes the newlines before and after the prefix
    # Given u'\n\n\n    # test comment\n    \n'
    # returns ([u'\n\n\n'], [u'    # test comment\n'], [u'    \n'])

    if not prefix:
        return (u'', u'', u'')

    # If there are no newlines, this was just a trailing comment. Leave it
    # alone.
    if not prefix.count(u'\n'):
        return (u'', prefix, u'')

    if prefix.count("#"):
        whitespace_before_first_comment = prefix[:prefix.index(u"#")]
        start_of_comment = whitespace_before_first_comment.rfind(u'\n')
        if prefix.rfind(u'\n') > prefix.index(u'#'):
            comments = u"%s\n" % prefix[start_of_comment + 1:].rstrip()
            # Add a single newline back if it was stripped
        else:
            comments = prefix[start_of_comment + 1:].rstrip()
    else:
        if prefix.count(u'\n'):
            comments = prefix.rsplit(u'\n')[1]
            # If no comments, there are no comments except the trailing spaces
            # before the current line
        else:
            comments = prefix
    comments_start = prefix.index(comments)
    return prefix[:comments_start].strip(u' '), comments, prefix[
        comments_start + len(comments):]


def get_quotes(text):
    # Returns the quote type start and end
    # Given u"ur'the string'" returns (u"ur'", u"'")

    if text[:2].lower() in [u'br', u'ur']:
        leading_chars = 2
    elif text[:1].lower() in [u'b', u'u', u'r']:
        leading_chars = 1
    else:
        leading_chars = 0

    if text[leading_chars:leading_chars + 3] in [u'"""', u"'''"]:
        # Triple-quoted string
        quote_start = text[:leading_chars + 3]
    else:
        # Single-quoted string
        quote_start = text[:leading_chars + 1]
    return (quote_start, quote_start[leading_chars:])


# Like TextWrapper, but for leaves
def wrap_leaves(nodes, width=MAX_CHARS, initial_indent=u'',
    subsequent_indent=u''):
    lines = []

    # Fake the prefix of the first node to be the indent that it should be.
    # We'll set it back afterward.
    first_node_prefix = nodes[0].prefix
    nodes[0].prefix = u' ' * nodes[0].column

    nodes.reverse()
    while nodes:

        curr_line = []
        curr_len = 0

        # Figure out which static string will prefix this line.
        if lines:
            indent = subsequent_indent
        else:
            indent = initial_indent

        # Maximum width for this line.
        curr_width = width - len(indent)

        while nodes:
            last_node = nodes[-1]

            if lines and not curr_line:
                # Strip prefixes for subsequent lines
                last_node.prefix = u''

            node_length = len(last_node.prefix) + len(last_node.value)

            # Can at least squeeze this chunk onto the current line.
            if curr_len + node_length <= curr_width:
                curr_line.append(nodes.pop())
                curr_len += node_length

            # Nope, this line is full.
            else:
                # only disallow breaking on/after equals if parent of this type
                if nodes and nodes[-1].type in [token.COMMA, token.EQUAL]:
                    # We don't want the next line to start on one of these
                    # tokens
                    node_to_move = curr_line.pop()
                    nodes.append(node_to_move)
                if (curr_line and curr_line[-1].type == token.EQUAL and
                    curr_line[-1].parent.type != symbols.expr_stmt):
                    # We don't want this line to end on one of these tokens
                    node_to_move = curr_line.pop()
                    nodes.append(node_to_move)
                    node_to_move = curr_line.pop()
                    nodes.append(node_to_move)
                break

        # The current line is full, and the next chunk is too big to fit on
        # *any* line (not just this one). TODO implement this at some point if
        # nodes and len(nodes[-1].value) + len(nodes[-1].prefix) > curr_width:
        # self._handle_long_word(nodes, curr_line, curr_len, width)

        if curr_line:
            curr_line[0].prefix = "%s%s" % (indent, curr_line[0].prefix)
            lines.append(curr_line)

    lines[0][0].prefix = first_node_prefix
    return lines
