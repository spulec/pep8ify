from __future__ import unicode_literals
from lib2to3.fixer_base import BaseFix
from .utils import node_text


def get_previous_node(node):
    """
    Return the node before this node.
    """
    if node.prev_sibling:
        return node.prev_sibling
    if node.parent:
        return get_previous_node(node.parent)


class FixWhitespaceBeforeInlineComment(BaseFix):
    '''
    Separate inline comments by at least two spaces.

    An inline comment is a comment on the same line as a statement.  Inline
    comments should be separated by at least two spaces from the statement.
    They should start with a # and a single space.
    '''

    def match(self, node):
        # An inline comment must contain with a #
        if not node.prefix.count("#"):
            return False

        # If the node's prefix starts with a newline, then this is not an
        # inline comment because there is not code before this.
        if node.prefix.lstrip(" \t").startswith("\n"):
            return False

        # If the previous node ended in a newline, then this node is
        # starting the line so it is not an inline comment.
        prev_node = get_previous_node(node)
        if not prev_node:
            # If no previous node, this is not an inline comment.
            return False
        prev_node_text = node_text(prev_node)
        if prev_node_text.endswith('\n'):
            return False

        return True

    def transform(self, node, results):
        position = node.prefix.find("#")
        if position > 2:
            # Already more than two spaces before comment
            whitespace_before, comment_after = node.prefix.split("#", 1)
            new_prefix = "%s# %s" % (whitespace_before, comment_after.lstrip(
            ))
        else:
            new_prefix = "  # %s" % node.prefix.replace("#", "", 1).lstrip()
        if node.prefix != new_prefix:
            node.prefix = new_prefix
            node.changed()
