from lib2to3.fixer_base import BaseFix
from lib2to3.pgen2 import token


class FixTrailingWhitespace(BaseFix):
    u''' Make sure that no lines in the file have trailing whitespace.'''
    
    _accept_type = token.NEWLINE
    
    def match(self, node):
        return node.prefix != u''
    
    def transform(self, node, results):
        node.prefix = node.prefix.rstrip()
        node.changed()
