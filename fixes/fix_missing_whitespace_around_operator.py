from lib2to3.fixer_base import BaseFix
#from lib2to3.pgen2 import token


class FixMissingWhitespaceAroundOperator(BaseFix):
    u''' No line should be greater than 80 characters.'''
    
    def match(self, node):
        return False
    
    def transform(self, node, results):
        pass
        # node.prefix = node.prefix.rstrip()
        # node.changed()
