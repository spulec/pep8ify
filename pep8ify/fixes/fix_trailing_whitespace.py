from lib2to3.fixer_base import BaseFix
from lib2to3.pgen2 import token


class FixTrailingWhitespace(BaseFix):
    u'''
    Trailing whitespace is superfluous.
    Except when it occurs as part of a blank line (i.e. the line is
    nothing but whitespace). According to Python docs[1] a line with only
    whitespace is considered a blank line, and is to be ignored. However,
    matching a blank line to its indentation level avoids mistakenly
    terminating a multi-line statement (e.g. class declaration) when
    pasting code into the standard Python interpreter.

    [1] http://docs.python.org/reference/lexical_analysis.html#blank-lines
    '''

    def match(self, node):
        # Newlines can be from a newline token or inside a node prefix
        if node.type == token.NEWLINE or node.prefix.count(u'\n'):
            return True

    def transform(self, node, results):
        if node.prefix.count(u'#'):
            prefix_split = node.prefix.split(u'\n')
            # Rstrip every line except for the last one, since that is the
            # whitespace before this line
            new_prefix = u'\n'.join([line.rstrip(u' \t') for line in
                prefix_split[:-1]] + [prefix_split[-1]])
        else:
            new_prefix = node.prefix.lstrip(u' \t')
        if node.prefix != new_prefix:
            node.prefix = new_prefix
            node.changed()
