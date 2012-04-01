from lib2to3.fixer_base import BaseFix
from lib2to3.pgen2 import token
from lib2to3.pytree import type_repr

from .utils import OPERATORS, BINARY_OPERATORS, UNARY_OPERATORS, is_leaf

class FixWhitespaceAroundOperator(BaseFix):
    u''' Avoid extraneous whitespace in the following situations:
    
    - More than one space around an assignment (or other) operator to
      align it with another.
    
    '''
    
    def match(self, node):
        if is_leaf(node) and node.value in OPERATORS:
            # Allow unary operators: -123, -x, +1.
            if node.value in UNARY_OPERATORS and type_repr(node.parent.type) == u'factor':
                return "rstrip"
            
            # Allow argument unpacking: foo(*args, **kwargs).
            if node.value in [u'*', u'**'] and type_repr(node.parent.type) in [u'arglist', u'varargslist', u'typedargslist'] \
                and (not node.prev_sibling or node.prev_sibling.type == token.COMMA):
                return "rstrip"
            
            # Allow keyword assignment: foobar(foo=bar)
            if node.value == u'=' and type_repr(node.parent.type) in [u'argument', u'arglist', u'typedargslist']:
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
