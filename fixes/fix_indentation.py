from lib2to3.fixer_base import BaseFix
#from lib2to3.pgen2 import token


class FixIndentation(BaseFix):
    u'''
    Use 4 spaces per indentation level.

    For really old code that you don't want to mess up, you can continue to
    use 8-space tabs.
    '''
    
    def match(self, node):
        return False
    
    def transform(self, node, results):
        pass
        # node.prefix = node.prefix.rstrip()
        # node.changed()
