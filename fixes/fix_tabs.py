from lib2to3.fixer_base import BaseFix

from .utils import is_leaf


class FixTabs(BaseFix):
    u''' Replace all tabs with spaces.'''
    
    def match(self, node):
        if node.prefix.count('\t') or (is_leaf(node)
            and node.value.count('\t')):
            return True
        return False
    
    def transform(self, node, results):
        node.prefix = node.prefix.replace('\t', u'    ')
        node.value = node.value.replace('\t', u'    ')
        node.changed()
