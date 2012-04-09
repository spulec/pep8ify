from lib2to3.fixer_base import BaseFix

from .utils import get_leaves_after_last_newline


class FixTrailingBlankLines(BaseFix):
    u'''
    Trailing blank lines are superfluous.
    '''
    
    order = "pre"
    first_time = True
    
    def match(self, node):
        if not self.first_time:
            return
        
        self.first_time = False
        leaves_after_last_newline = get_leaves_after_last_newline(node)
        # Return any leaves with newlines.
        return [leaf for leaf in leaves_after_last_newline
                    if leaf.prefix.count('\n')]
    
    def transform(self, node, results):
        for index, result in enumerate(results):
            if index:
                # We've already stripped one newline. Strip any remaining
                result.prefix = result.prefix.rstrip()
                result.changed()
            else:
                # We haven't stripped any newlines yet. We need to strip all
                # whitespace, but leave a signle newline.
                result.prefix = u'%s%s' % ('\n', result.prefix.rstrip())
                result.changed()
