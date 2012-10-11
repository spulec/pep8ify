from lib2to3.fixer_base import BaseFix
from lib2to3.pytree import Leaf
from lib2to3.pgen2 import token

from .utils import prefix_indent_count


class FixIndentation(BaseFix):
    u'''
    Use 4 spaces per indentation level.

    For really old code that you don't want to mess up, you can continue to
    use 8-space tabs.
    '''

    indents = []
    line_num = 0
    prev_line_indent = 0

    def __init__(self, options, log):
        self.indents = []
        self.line_num = 0
        # This is the indent of the previous line before it was modified
        self.prev_line_indent = 0

        super(FixIndentation, self).__init__(options, log)

    def match(self, node):
        if isinstance(node, Leaf):
            return True
        return False

    def transform(self, node, results):
        if node.type == token.INDENT:
            self.transform_indent(node)
        elif node.type == token.DEDENT:
            self.transform_outdent(node)
        elif self.line_num != node.lineno:
            self.transform_newline(node)

    def transform_indent(self, node):
        self.line_num = node.lineno
        # Indent spacing is stored in the value, node the prefix
        self.prev_line_indent = len(node.value.replace(u'\t', u' ' * 4))
        self.indents.append(self.prev_line_indent)

        new_value = u' ' * 4 * len(self.indents)

        new_prefix = node.prefix
        # Strip any previous newlines since they shouldn't change the comment
        # indent
        comment_indent = node.prefix.strip(u'\n').find(u"#")
        if comment_indent > -1:
            # Determine if we should align the comment with the line before or
            # after
            if comment_indent == node.next_sibling.leaves().next().column:
                # This comment should be aligned with its next_sibling
                new_comment_indent = new_value
            else:
                # This comment should be aligned with the previous indent
                new_comment_indent = u' ' * 4 * (len(self.indents) - 1)

            # Split the lines of comment and prepend them with the new indent
            # value
            new_prefix = ('\n'.join([u"%s%s" % (new_comment_indent, line.
                lstrip()) if line else u'' for line in new_prefix.split('\n')]
            ).rstrip(u' '))

        if node.value != new_value or node.prefix != new_prefix:
            node.value = new_value
            node.prefix = new_prefix
            node.changed()

    def transform_outdent(self, node):
        self.line_num = node.lineno
        self.prev_line_indent = prefix_indent_count(node)

        if node.column:
            # Partial outdent, remove higher indents
            tab_count = node.prefix.count(u'\t')
            if tab_count:
                # If tabs, indent level is number of tabs
                indent_level = tab_count * 4
            else:
                indent_level = node.column
            self.indents = self.indents[:self.indents.index(indent_level) + 1]
            # For OUTDENTS, the indentation is in the last line of the prefix
            self.fix_indent_prefix(node)
        else:
            # Outdent all the way
            self.indents = []

    def transform_newline(self, node):
        self.line_num = node.lineno
        if self.indents:
            self.fix_indent_prefix(node, newline=True)
        else:
            # First line, no need to do anything
            pass

    def fix_indent_prefix(self, node, newline=False):
        if node.prefix:
            new_indent = len(self.indents)
            if newline:
                # Don't reindent continuing lines that are already indented
                # past where they need to be.
                current_indent = prefix_indent_count(node)
                if current_indent > self.prev_line_indent:
                    return

            prefix_lines = node.prefix.split('\n')[:-1]
            prefix_lines.append(u' ' * 4 * new_indent)
            new_prefix = '\n'.join(prefix_lines)
            if node.prefix != new_prefix:
                node.prefix = new_prefix
                node.changed()
