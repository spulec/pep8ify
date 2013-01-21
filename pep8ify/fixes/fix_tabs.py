from __future__ import unicode_literals
from lib2to3.fixer_base import BaseFix
from lib2to3.pytree import Leaf


class FixTabs(BaseFix):
    '''
    For new projects, spaces-only are strongly recommended over tabs.  Most
    editors have features that make this easy to do.
    '''

    def match(self, node):
        if node.prefix.count('\t') or (isinstance(node, Leaf)
            and node.value.count('\t')):
            return True
        return False

    def transform(self, node, results):
        new_prefix = node.prefix.replace('\t', '    ')
        new_value = node.value.replace('\t', '    ')
        if node.prefix != new_prefix or node.value != new_value:
            node.prefix = new_prefix
            node.value = new_value
            node.changed()
