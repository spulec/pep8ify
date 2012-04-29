from lib2to3.fixer_base import BaseFix
from lib2to3.pgen2 import token

LSTRIP_TOKENS = [token.LPAR, token.LSQB, token.LBRACE]
RSTRIP_TOKENS = [token.RPAR, token.RSQB, token.COLON, token.COMMA, token.SEMI,
    token.RBRACE]
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
        if node.type in LSTRIP_TOKENS and node.get_suffix():
            new_prefix = node.next_sibling.prefix.lstrip(u' \t')
            if node.next_sibling.prefix != new_prefix:
                node.next_sibling.prefix = new_prefix
                node.next_sibling.changed()
        elif node.type in RSTRIP_TOKENS:
            new_prefix = node.prefix.rstrip(u' \t')
            if node.prefix != new_prefix:
                node.prefix = new_prefix
                node.changed()
