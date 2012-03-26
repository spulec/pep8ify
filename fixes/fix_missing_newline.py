from lib2to3.fixer_base import BaseFix
from lib2to3.pgen2 import token


class FixMissingNewline(BaseFix):
    u''' Make sure that the file ends in a newline. This is somewhat tricky\
        since the parse tree sometimes categorizes newlines as token.DEDENTs'''
    
    #_accept_type = token.NEWLINE
    order = "pre"
    first_time = True
    
    def match(self, node):
        if not self.first_time:
            return
        
        self.first_time = False
        all_leaves = []
        for leaf in node.leaves():
            all_leaves.append(leaf)
        last_newline_leaf_index = -1
        for index, leaf in enumerate(all_leaves):
            if leaf.type == token.NEWLINE:
                last_newline_leaf_index = index
        # Get all of the leaves after the last newline leaf
        leaves_after_last_newline = all_leaves[last_newline_leaf_index + 1:]
        if not any(leaf.prefix.count('\n')
                   for leaf in leaves_after_last_newline):
            # If none of those have a prefix containing a newline,
            # we need to add one
            return leaves_after_last_newline[0]
    
    def transform(self, node, results):
        results.prefix = u'\n'
        results.changed()
