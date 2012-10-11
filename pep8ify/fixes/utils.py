from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as symbols
from lib2to3.pytree import Leaf

BINARY_OPERATORS = frozenset(['**=', '*=', '+=', '-=', '!=', '<>',
    '%=', '^=', '&=', '|=', '==', '/=', '//=', '<=', '>=', '<<=', '>>=',
    '%', '^', '&', '|', '=', '/', '//', '<', '>', '<<'])
UNARY_OPERATORS = frozenset(['>>', '**', '*', '+', '-'])
OPERATORS = BINARY_OPERATORS | UNARY_OPERATORS
MAX_CHARS = 79


def get_leaves_after_last_newline(node):
    # Get all of the leaves after the last newline leaf
    all_leaves = []
    last_newline_leaf_index = -1
    for index, leaf in enumerate(node.leaves()):
        all_leaves.append(leaf)
        if leaf.type == token.NEWLINE:
            last_newline_leaf_index = index
    return all_leaves[last_newline_leaf_index + 1:]


def first_child_leaf(node):
    if isinstance(node, Leaf):
        return node
    elif node.children:
        return first_child_leaf(node.children[0])
    else:
        return None


def node_text(node):
    result = u""
    if isinstance(node, Leaf):
        result += node.value
    elif node.children:
        for child in node.children:
            result += node_text(child)
    return result


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


def node_length(*nodes):
    return sum(len(node.prefix.strip(u'\n\t')) +
        len(node.value.strip(u'\n\t')) for node in nodes)


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
        if prefix.count(u'\n') and not prefix.split(u'\n')[-1].strip():
            # Add a single newline back if there was a newline in the ending
            # whitespace
            comments = u"%s\n" % prefix[start_of_comment + 1:].rstrip()
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
        tracking_back = False
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

            curr_node_length = node_length(last_node)

            # Can at least squeeze this chunk onto the current line.
            if curr_len + curr_node_length <= curr_width:
                curr_line.append(nodes.pop())
                curr_len += curr_node_length

            # Nope, this line is full.
            else:
                # only disallow breaking on/after equals if parent of this type
                if nodes and nodes[-1].type in [token.COMMA, token.EQUAL]:
                    # We don't want the next line to start on one of these
                    # tokens
                    tracking_back = True
                    nodes.append(curr_line.pop())
                if (curr_line and curr_line[-1].type == token.EQUAL and
                    curr_line[-1].parent.type != symbols.expr_stmt):
                    # We don't want this line to end on one of these tokens.
                    # Move the last two nodes back onto the list
                    tracking_back = True
                    nodes.extend(reversed(curr_line[-2:]))
                    del curr_line[-2:]
                break

        # The current line is full, and the next chunk is too big to fit on
        # *any* line (not just this one).
        if nodes:
            next_chunk_length = node_length(nodes[-1])
            if tracking_back:
                next_chunk_length += node_length(nodes[-2])
            if next_chunk_length > curr_width:
                curr_line.append(nodes.pop())
                if nodes and nodes[-1].type in [token.COMMA, token.EQUAL]:
                    # We don't want the next line to start on these chars, just
                    # add them here Check maximum_line_length3_in:4 for an
                    # example
                    curr_line.append(nodes.pop())
            elif (len(nodes) > 2 and not curr_line and
                node_length(*nodes[-3:]) > curr_width):
                # This scenario happens when we were not able to break on an
                # assignment statement above and the next line is still too
                # long. Remove the last 3 nodes and move them to curr_line
                curr_line.extend(reversed(nodes[-3:]))
                del nodes[-3:]
                if nodes and nodes[-1].type in [token.COMMA, token.EQUAL]:
                    curr_len += node_length(nodes[-1])
                    curr_line.append(nodes.pop())

        if curr_line:
            curr_line[0].prefix = "%s%s" % (indent, curr_line[0].prefix)
            lines.append(curr_line)
        else:
            assert False, ("There was an error parsing this line."
                "Please report this to the package owner.")

    lines[0][0].prefix = first_node_prefix
    return lines
