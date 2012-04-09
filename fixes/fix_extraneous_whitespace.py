from lib2to3.fixer_base import BaseFix
from lib2to3.pgen2 import token


class FixExtraneousWhitespace(BaseFix):
    u'''
    Avoid extraneous whitespace in the following situations:

    - Immediately inside parentheses, brackets or braces.

    - Immediately before a comma, semicolon, or colon.
    '''
    
    def match(self, node):
        if node.type in (token.LPAR, token.LSQB, token.LBRACE):
            return 'rstrip'
        elif node.type in (token.RPAR, token.RSQB, token.COLON, token.COMMA, token.SEMI, token.RBRACE):
            return 'lstrip'
        return False
    
    def transform(self, node, results):
        if results == 'rstrip' and node.get_suffix():
            node.next_sibling.prefix = node.next_sibling.prefix.rstrip()
            node.next_sibling.changed()
        elif results == 'lstrip':
            node.prefix = node.prefix.lstrip()
            node.changed()
