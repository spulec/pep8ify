from lib2to3.fixer_base import BaseFix
from lib2to3.pygram import python_symbols as symbols

from .utils import get_leaves_after_last_newline


class FixMissingNewline(BaseFix):
    u'''
    The last line should have a newline.

    This is somewhat tricky since the parse tree
    sometimes categorizes newlines as token.DEDENTs
    '''

    def match(self, node):
        # We only want to work with the top-level input since this should only
        # run once.
        if node.type != symbols.file_input:
            return

        leaves_after_last_newline = get_leaves_after_last_newline(node)
        if not any(leaf.prefix.count('\n')
                   for leaf in leaves_after_last_newline):
            # If none of those have a prefix containing a newline,
            # we need to add one
            return leaves_after_last_newline[0]

    def transform(self, node, leaf):
        if leaf.prefix != u'\n':
            leaf.prefix = u'\n'
            leaf.changed()
