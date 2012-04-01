from lib2to3.fixer_base import BaseFix
from lib2to3.pgen2 import token
from lib2to3.pytree import Node, Leaf
from lib2to3.pygram import python_symbols

from .utils import is_leaf


# TODO remove all type_repr shit

class FixImportsOnSeparateLines(BaseFix):
    u''' No line should be greater than 80 characters.
    Imports should usually be on separate lines.
    
    '''
    
    def match(self, node):
        if node.type == python_symbols.simple_stmt and node.children[0].type == python_symbols.import_name \
            and node.children[0].children[1].type == python_symbols.dotted_as_names:
            return node.children[0].children[1].children
        return False
    
    def transform(self, node, results):
        child_imports = [leaf.value for leaf in results if leaf.type == token.NAME]
        
        new_nodes = [Node(python_symbols.simple_stmt, [Node(python_symbols.import_name, [Leaf(1, u'import'), Leaf(1, module_name, prefix=u" ")]), Leaf(4, u'\n')]) 
            for module_name in child_imports]
        node.replace(new_nodes)
        node.changed()
