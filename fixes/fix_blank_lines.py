from lib2to3.fixer_base import BaseFix
#from lib2to3.pgen2 import token


class FixBlankLines(BaseFix):
    u'''
    Separate top-level function and class definitions with two blank lines.

    Method definitions inside a class are separated by a single blank line.

    Extra blank lines may be used (sparingly) to separate groups of related
    functions.  Blank lines may be omitted between a bunch of related
    one-liners (e.g. a set of dummy implementations).

    Use blank lines in functions, sparingly, to indicate logical sections.

    '''
    
    def match(self, node):
        #import pdb;pdb.set_trace()
        return False
    
    def transform(self, node, results):
        pass
        # node.prefix = node.prefix.rstrip()
        # node.changed()
