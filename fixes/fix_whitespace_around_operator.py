from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Leaf
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as symbols

from .utils import OPERATORS, UNARY_OPERATORS

class FixWhitespaceAroundOperator(BaseFix):
    u'''
    Avoid extraneous whitespace in the following situations:
    
    - More than one space around an assignment (or other) operator to
      align it with another.
    '''
    
    def match(self, node):
        if isinstance(node, Leaf) and node.value in OPERATORS:
            # Allow unary operators: -123, -x, +1.
            if node.value in UNARY_OPERATORS and node.parent.type == symbols.factor:
                return "rstrip"
            
            # Allow argument unpacking: foo(*args, **kwargs).
            arg_symbols = [symbols.arglist, symbols.varargslist, symbols.typedargslist]
            if (node.value in [u'*', u'**'] and node.parent.type in arg_symbols
                and (not node.prev_sibling or node.prev_sibling.type == token.COMMA)):
                return "rstrip"
            
            # Allow keyword assignment: foobar(foo=bar)
            keyword_arg_symbols = [symbols.argument, symbols.arglist, symbols.typedargslist]
            if node.value == u'=' and node.parent.type in keyword_arg_symbols:
                return "no_spaces"
            
            # Finally check if the spacing actually needs fixing
            if (node.prefix != u" " or node.get_suffix() != u" "):
                return "spaces"
        return False
    
    def transform(self, node, results):
        if results == "spaces":
            pre_spacing = u" "
            post_spacing = u" "
        elif results == "rstrip":
            # If 'rstrip', just set prefix back to itself
            pre_spacing = node.prefix
            post_spacing = u""
        else:
            pre_spacing = u""
            post_spacing = u""
        node.prefix = pre_spacing
        node.next_sibling.prefix = post_spacing
        node.changed()
        node.next_sibling.changed()
