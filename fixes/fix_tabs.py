from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Leaf


class FixTabs(BaseFix):
    u''' Replace all tabs with spaces.'''
    
    def match(self, node):
        if node.prefix.count('\t') or (isinstance(node, Leaf)
            and node.value.count('\t')):
            return True
        return False
    
    def transform(self, node, results):
        node.prefix = node.prefix.replace('\t', u'    ')
        node.value = node.value.replace('\t', u'    ')
        node.changed()
