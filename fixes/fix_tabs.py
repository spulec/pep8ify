from lib2to3.fixer_base import BaseFix


class FixTabs(BaseFix):
    u''' Replace all tabs with spaces.'''
    
    def match(self, node):
        if node.prefix.count('\t') or (hasattr(node, 'value')
            and node.value.count('\t')):
            return True
        return False
    
    def transform(self, node, results):
        node.prefix = node.prefix.replace('\t', '    ')
        node.value = node.value.replace('\t', '    ')
        node.changed()
