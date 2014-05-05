from __future__ import unicode_literals
from lib2to3.fixer_base import BaseFix
from lib2to3.pytree import Leaf
from lib2to3.pgen2 import token

import re

from .utils import prefix_indent_count, IS_26, add_leaves_method, NUM_SPACES, SPACES


class FixIndentation(BaseFix):
    """
    Use 4 spaces per indentation level.

    For really old code that you don't want to mess up, you can continue to
    use 8-space tabs.
    """

    def __init__(self, options, log):
        self.indents = []
        self.indent_level = 0
        self.line_num = 0
        self.current_line_dedent = None
        # This is the indent of the previous line before it was modified
        self.prev_line_indent = 0

        super(FixIndentation, self).__init__(options, log)

    def match(self, node):
        if isinstance(node, Leaf):
            return True
        return False

    def transform(self, node, results):
        if node.type == token.INDENT:
            self.current_line_dedent = None
            self.transform_indent(node)
        elif node.type == token.DEDENT:
            self.transform_outdent(node)
        elif self.line_num != node.lineno:
            self.current_line_dedent = None
            self.transform_newline(node)

    def transform_indent(self, node):
        if IS_26:
            node = add_leaves_method(node)
        self.line_num = node.lineno
        # Indent spacing is stored in the value, node the prefix
        self.prev_line_indent = len(node.value.replace('\t', SPACES))
        self.indents.append(self.prev_line_indent)
        self.indent_level += 1

        new_value = SPACES * self.indent_level
        new_prefix = '\n'.join(self.align_preceding_comment(node)).rstrip(' ')

        if node.value != new_value or node.prefix != new_prefix:
            node.value = new_value
            node.prefix = new_prefix
            node.changed()

    def transform_outdent(self, node):
        if self.line_num == node.lineno:
            # If a line dedents more then one level (so it's a
            # multi-level dedent), there are several DEDENT nodes.
            # These have the same lineno, but only the very first one
            # has a prefix, the others must not.
            is_consecutive_indent = True
            assert not node.prefix # must be empty
            assert (self.current_line_dedent is None or
                    self.current_line_dedent.lineno == node.lineno)
        else:
            is_consecutive_indent = False
            self.current_line_dedent = node
            assert node.prefix or node.column == 0 # must not be empty

        self.line_num = node.lineno
        self.prev_line_indent = prefix_indent_count(node)

        # outdent, remove highest indent
        self.indent_level -= 1
        # if the last node was a dedent, too, modify that node's prefix
        # and remember that node
        self.fix_indent_prefix(self.current_line_dedent,
                               not is_consecutive_indent)
        # pop indents *after* prefix/comment has been reindented,
        # as the last indent-level may be needed there.
        self.indents.pop()


    def transform_newline(self, node):
        self.line_num = node.lineno
        if self.indent_level:
            # Don't reindent continuing lines that are already indented
            # past where they need to be.
            current_indent = prefix_indent_count(node)
            if current_indent <= self.prev_line_indent:
                self.fix_indent_prefix(node)
        else:
            # First line, no need to do anything
            pass

    def align_preceding_comment(self, node):
        prefix = node.prefix
        # Strip any previous empty lines since they shouldn't change
        # the comment indent
        comment_indent = re.sub(r'^([\s\t]*\n)?', '', prefix).find("#")
        if comment_indent > -1:
            # Determine if we should align the comment with the line before or
            # after
            # Default: indent to current level
            new_comment_indent = SPACES * self.indent_level

            if (node.type == token.INDENT and
                comment_indent < next(node.next_sibling.leaves()).column):
                # The comment is not aligned with the next indent, so
                # it should be aligned with the previous indent.
                new_comment_indent = SPACES * (self.indent_level - 1)
            elif node.type == token.DEDENT:
                # The comment is not aligned with the previous indent, so
                # it should be aligned with the next indent.
                try:
                    level = self.indents.index(comment_indent) + 1
                    new_comment_indent = level * SPACES
                except ValueError:
                    new_comment_indent = comment_indent * ' '
                    # indent of comment does not match an indent level
                    if comment_indent < self.indents[0]:
                        # not even at indent level 1, leave unchanged
                        new_comment_indent = comment_indent * ' '
                    else:
                        i = max(i for i in self.indents if i < comment_indent)
                        level = self.indents.index(i) + 1
                        new_comment_indent = (level * SPACES
                                              + (comment_indent-i) * ' ')

            # Split the lines of comment and prepend them with the new indent
            # value
            return [(new_comment_indent + line.lstrip()) if line else ''
                    for line in prefix.split('\n')]
        else:
            return prefix.split('\n')


    def fix_indent_prefix(self, node, align_comments=True):
        if node.prefix:

            if align_comments:
                prefix_lines = self.align_preceding_comment(node)[:-1]
            else:
                prefix_lines = node.prefix.split('\n')[:-1]
            prefix_lines.append(SPACES * self.indent_level)
            new_prefix = '\n'.join(prefix_lines)
            if node.prefix != new_prefix:
                node.prefix = new_prefix
                node.changed()
