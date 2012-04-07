from lib2to3.fixer_base import BaseFix
#from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols

from .utils import get_whitespace_before_definition, has_parent, tuplize_comments


class FixBlankLines(BaseFix):
    u'''
    Separate top-level function and class definitions with two blank lines.

    Method definitions inside a class are separated by a single blank line.

    Extra blank lines may be used (sparingly) to separate groups of related
    functions.  Blank lines may be omitted between a bunch of related
    one-liners (e.g. a set of dummy implementations).

    Use blank lines in functions, sparingly, to indicate logical sections.
    
    '''
    #temp = False
    #TODO add 6 blank lines on line 28
    
    def match(self, node):
        # if hasattr(node, 'value') and node.value == "testing2":
        #     import pdb;pdb.set_trace()
        #     self.temp = True
        # 
        # if self.temp:
        #     import pdb;pdb.set_trace()
        
        # Get classes, non-decorateds funcs and decorators. Ignore decorateds funcs
        # since they will be taken care of with the decorator.
        if (node.type == python_symbols.funcdef and node.parent.type != python_symbols.decorated) \
            or node.type == python_symbols.classdef or node.type == python_symbols.decorated or node.type == python_symbols.simple_stmt:
            return True
        return False
    
    def transform(self, node, results):
        
        # Sometimes newlines are in prefix of current node, sometimes they're in prefix of the prev sibling
        if node.prefix:
            using_node_prefix = True
            previous_whitespace = node.prefix
        else:
            using_node_prefix = False
            whitespace_before_def = get_whitespace_before_definition(node)
            if not whitespace_before_def:
                # No previous node, must be the first node.
                return
            previous_whitespace = whitespace_before_def.prefix
        
        before_comments, comments, after_comments = tuplize_comments(previous_whitespace)
        
        if node.type == python_symbols.simple_stmt or has_parent(node, python_symbols.simple_stmt):
            max_lines_between_defs = 1
            min_lines_between_defs = 0
        elif has_parent(node, python_symbols.classdef) or has_parent(node, python_symbols.funcdef):
            # If we're inside a definition, only use a single space
            max_lines_between_defs = 1
            min_lines_between_defs = 1
        else:
            # Top-level definition
            max_lines_between_defs = 2
            min_lines_between_defs = 2
        
        if len(before_comments) > max_lines_between_defs:
            before_comments = u'\n' * max_lines_between_defs
        if len(after_comments) > max_lines_between_defs:
            after_comments = u'\n' * max_lines_between_defs
        
        if len(before_comments) + len(after_comments) > max_lines_between_defs:
            if before_comments and after_comments:
                # If there are spaces before and after, trim them down on both sides
                # to either 1 before and 1 after or 0 before and 1 after.
                before_comments = u'\n' * (min_lines_between_defs - 1) if min_lines_between_defs else u''
                after_comments = u'\n'
        
        comment_lines = len(before_comments) + len(after_comments)
        if comment_lines < min_lines_between_defs:
            before_comments += (min_lines_between_defs - comment_lines) * u'\n'
        
        if using_node_prefix:
            node.prefix = u'%s%s%s' % (before_comments, comments, after_comments)
            node.changed()
        else:
            whitespace_before_def.prefix = u'%s%s%s' % (before_comments, comments, after_comments)
            whitespace_before_def.changed()


def newlines_before_comments(split_lines):
    for index, line in enumerate(split_lines):
        if line != u'':
            return index
