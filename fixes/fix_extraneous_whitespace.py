from lib2to3.fixer_base import BaseFix
#from lib2to3.pgen2 import token


class FixExtraneousWhitespace(BaseFix):
    u''' No line should be greater than 80 characters.'''
    
    def match(self, node):
        if node.type in (7, 9, 26):
            return 'rstrip'
        elif node.type in (8, 10, 11, 12, 27):
            return 'lstrip'
        return False
        # LPAR = 7
        # RPAR = 8
        # LSQB = 9
        # RSQB = 10
        # LBRACE = 26
        # RBRACE = 27
        # COLON = 11
        # COMMA = 12
    
    def transform(self, node, results):
        if results == 'rstrip' and node.get_suffix():
            node.next_sibling.prefix = node.next_sibling.prefix.rstrip()
            node.next_sibling.changed()
        elif results == 'lstrip':
            node.prefix = node.prefix.lstrip()
            node.changed()
