from lib2to3.fixer_util import Leaf
from lib2to3.pgen2 import token

BINARY_OPERATORS = frozenset(['**=', '*=', '+=', '-=', '!=', '<>',
    '%=', '^=', '&=', '|=', '==', '/=', '//=', '<=', '>=', '<<=', '>>=',
    '%',  '^',  '&',  '|',  '=',  '/',  '//',  '<',  '>',  '<<'])
UNARY_OPERATORS = frozenset(['>>', '**', '*', '+', '-'])
OPERATORS = BINARY_OPERATORS | UNARY_OPERATORS


def is_leaf(node):
    return hasattr(node, 'value')
    # TODO: replace all of these with `if isinstance(node, Leaf):`


def get_leaves_after_last_newline(node):
    # Get all of the leaves after the last newline leaf
    all_leaves = []
    for leaf in node.leaves():
        all_leaves.append(leaf)
    last_newline_leaf_index = -1
    for index, leaf in enumerate(all_leaves):
        if leaf.type == token.NEWLINE:
            last_newline_leaf_index = index
    leaves_after_last_newline = all_leaves[last_newline_leaf_index + 1:]
    return leaves_after_last_newline


def get_whitespace_before_definition(node):
    if node.prev_sibling:
        return get_last_child(node.prev_sibling)


def get_last_child(node):
    if isinstance(node, Leaf):
        return node
    else:
        return get_last_child(node.children[-1])


def has_parent(node, symbol_type):
    # Returns if node has a parent of type symbol_type
    if node.parent:
        return node.parent.type == symbol_type or has_parent(node.parent, symbol_type)

def tuplize_comments(prefix):
    # This tuplizes the newlines before and after the prefix
    # Given u'\n\n\n    # test comment\n    ', returns ([u'\n\n\n'], [u'# test comment\n    '], [u''])
    # We strip the last newline after a set of comments since it doesn't cound toward line counts

    #TODO this needs to be improved to handle spaces between nelines, ie u'\n    \n    #comment\n    '

    if not prefix:
        return (u'', u'', u'')

    if prefix.count("#"):
        comments = (u"%s\n" % prefix.lstrip(u'\n').rstrip(u'\n')) if prefix[-1] == u'\n' else prefix.lstrip(u'\n').rstrip(u'\n')  # Leave the trailing newline from the comment per the docstring
    else:
        if prefix.count(u'\n'):
            comments = prefix.rsplit(u'\n')[1]  # If no comments, there are no comments except the trailing spaces before the current line
        else:
            comments = prefix
    comments_start = prefix.index(comments)
    return prefix[:comments_start], comments, prefix[comments_start + len(comments):]


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
