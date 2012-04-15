from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Leaf
from lib2to3.pgen2 import token


class FixIndentation(BaseFix):
    u'''
    Use 4 spaces per indentation level.

    For really old code that you don't want to mess up, you can continue to
    use 8-space tabs.
    '''
    
    indents = []
    line_num = 0
    
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
        self.indents.append(len(node.value.replace(u'\t', u' ' * 4)))
        new_value = u' ' * 4 * len(self.indents)

        new_prefix = node.prefix
        comment_indent = node.prefix.find(u"#")
        if comment_indent > -1:
            # Determine if we should align the comment with the line before or after
            if comment_indent == node.next_sibling.leaves().next().column:
                # This comment should be aligned with its next_sibling
                new_comment_indent = new_value
            else:
                # This comment should be aligned with the previous indent
                new_comment_indent = u' ' * 4 * (len(self.indents) - 1)

            # Split the lines of comment and prepend them with the new indent value
            new_prefix = '\n'.join([u"%s%s" % (new_comment_indent, line.lstrip()) if line else u'' for line in new_prefix.split('\n')]).rstrip(u' ')

        if node.value != new_value or node.prefix != new_prefix:
            node.value = new_value
            node.prefix = new_prefix
            node.changed()

    def transform_outdent(self, node):
        self.line_num = node.lineno
        if node.column:
            # Partial outdent, remove higher indents
            self.indents = self.indents[:self.indents.index(node.column) + 1]
            # For OUTDENTS, the indentation is in the last line of the prefix
            self.fix_indent_prefix(node)
        else:
            # Outdent all the way
            self.indents = []

    def transform_newline(self, node):
        self.line_num = node.lineno
        if self.indents:
            self.fix_indent_prefix(node)
        else:
            # First line, no need to do anything
            pass

    def fix_indent_prefix(self, node):
        if node.prefix:
            prefix_lines = node.prefix.split('\n')[:-1]
            prefix_lines.append(u' ' * 4 * len(self.indents))
            new_prefix = '\n'.join(prefix_lines)
            if node.prefix != new_prefix:
                node.prefix = new_prefix
                node.changed()
