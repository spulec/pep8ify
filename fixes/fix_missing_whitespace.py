from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Newline
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as symbols


class FixMissingWhitespace(BaseFix):
    u'''
    Each comma, semicolon or colon should be followed by whitespace.
    '''

    def match(self, node):
        if (node.type in (token.COLON, token.COMMA, token.SEMI) and node.
            get_suffix() != u" "):
            # If there is a newline after, no space
            if (node.get_suffix().find(u'\n') == 0 or
                (node.next_sibling and node.next_sibling.children and
                node.next_sibling.children[0] == Newline())):
                return False
            # If we are using slice notation, no space necessary
            if node.parent.type in [symbols.subscript, symbols.sliceop]:
                return False
            # If a tuple with a single element, no space
            if not node.next_sibling:
                return False
            return True
        return False

    def transform(self, node, results):
        new_prefix = u" %s" % node.next_sibling.prefix.lstrip(u' \t')
        if node.next_sibling.prefix != new_prefix:
            node.next_sibling.prefix = new_prefix
            node.next_sibling.changed()
