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
