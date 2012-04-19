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
    
    _accept_type = token.NEWLINE
    
    def match(self, node):
        return node.prefix != u''
    
    def transform(self, node, results):
        new_prefix = node.prefix.rstrip()
        if node.prefix != new_prefix:
            node.prefix = new_prefix
            node.changed()
