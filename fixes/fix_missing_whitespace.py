from lib2to3.fixer_base import BaseFix
from lib2to3.pgen2 import token
from lib2to3.pytree import type_repr


class FixMissingWhitespace(BaseFix):
    u''' Each comma, semicolon or colon should be followed by whitespace.'''
    
    def match(self, node):
        if node.type in (token.COLON, token.COMMA, token.SEMI) and node.get_suffix() != u" ":
            # If we are using slice notation, no space necessary
            if type_repr(node.parent.type) in ('subscript', 'sliceop'):
                return False
            # If a tuple with a single element, no space
            if not node.next_sibling:
                return False
            return True
        return False
    
    def transform(self, node, results):
        node.next_sibling.prefix = u" "
        node.next_sibling.changed()
