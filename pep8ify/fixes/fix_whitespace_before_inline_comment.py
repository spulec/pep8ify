from __future__ import unicode_literals
from lib2to3.fixer_base import BaseFix


class FixWhitespaceBeforeInlineComment(BaseFix):
    '''
    Separate inline comments by at least two spaces.

    An inline comment is a comment on the same line as a statement.  Inline
    comments should be separated by at least two spaces from the statement.
    They should start with a # and a single space.
    '''

    def match(self, node):
        if (node.prefix.count("#") and
            not node.prefix.lstrip(" \t").startswith("\n")):
            # If the node starts with a comment and not a newline, then it is
            # an inline comment.
            return True
        return False

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
