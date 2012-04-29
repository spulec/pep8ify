from lib2to3.fixer_base import BaseFix
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as symbols


class FixWhitespaceBeforeParameters(BaseFix):
    u'''
    Avoid extraneous whitespace in the following situations:

    - Immediately before the open parenthesis that starts the argument
      list of a function call.

    - Immediately before the open parenthesis that starts an indexing or
      slicing.
    '''

    def match(self, node):
        if (node.type in (token.LPAR, token.LSQB) and node.parent.type ==
            symbols.trailer):
            return True
        return False

    def transform(self, node, results):
        if node.prefix != u"":
            node.prefix = u""
            node.changed()
