from lib2to3.fixer_base import BaseFix

from .utils import get_leaves_after_last_newline


class FixMissingNewline(BaseFix):
    u''' Make sure that the file ends in a newline. This is somewhat tricky
        since the parse tree sometimes categorizes newlines as token.DEDENTs'''
    
    #_accept_type = token.NEWLINE
    order = "pre"
    first_time = True
    
    def match(self, node):
        if not self.first_time:
            return
        
        self.first_time = False
        leaves_after_last_newline = get_leaves_after_last_newline(node)
        if not any(leaf.prefix.count('\n')
                   for leaf in leaves_after_last_newline):
            # If none of those have a prefix containing a newline,
            # we need to add one
            return leaves_after_last_newline[0]
    
    def transform(self, node, leaf):
        leaf.prefix = u'\n'
        leaf.changed()
