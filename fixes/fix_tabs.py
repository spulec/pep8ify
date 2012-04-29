from lib2to3.fixer_base import BaseFix
from lib2to3.pytree import Leaf


class FixTabs(BaseFix):
    u'''
    For new projects, spaces-only are strongly recommended over tabs.  Most
    editors have features that make this easy to do.
    '''

    def match(self, node):
        if node.prefix.count(u'\t') or (isinstance(node, Leaf)
            and node.value.count(u'\t')):
            return True
        return False

    def transform(self, node, results):
        new_prefix = node.prefix.replace(u'\t', u'    ')
        new_value = node.value.replace(u'\t', u'    ')
        if node.prefix != new_prefix or node.value != new_value:
            node.prefix = new_prefix
            node.value = new_value
            node.changed()
