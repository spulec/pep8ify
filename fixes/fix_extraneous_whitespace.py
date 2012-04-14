from lib2to3.fixer_base import BaseFix
from lib2to3.pgen2 import token

RSTRIP_TOKENS = [token.LPAR, token.LSQB, token.LBRACE]
LSTRIP_TOKENS = [token.RPAR, token.RSQB, token.COLON, token.COMMA, token.SEMI, token.RBRACE]
STRIP_TOKENS = RSTRIP_TOKENS + LSTRIP_TOKENS


class FixExtraneousWhitespace(BaseFix):
    u'''
    Avoid extraneous whitespace in the following situations:

    - Immediately inside parentheses, brackets or braces.

    - Immediately before a comma, semicolon, or colon.
    '''
    
    def match(self, node):
        if node.type in STRIP_TOKENS:
            return True
        return False
    
    def transform(self, node, results):
        if node.type in RSTRIP_TOKENS and node.get_suffix():
            node.next_sibling.prefix = node.next_sibling.prefix.rstrip()
            node.next_sibling.changed()
        elif node.type in LSTRIP_TOKENS:
            node.prefix = node.prefix.lstrip()
            node.changed()
