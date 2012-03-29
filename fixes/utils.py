from lib2to3.pgen2 import token


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
