from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import find_indentation
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as symbols

from .utils import (get_whitespace_before_definition, has_parent,
    tuplize_comments)


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
        # Get classes, non-decorateds funcs, decorators, and simple statements.
        # Ignore decorateds funcs since they will be taken care of with the
        # decorator.
        if (node.type == symbols.funcdef and node.parent.type != symbols.
            decorated or node.type == symbols.classdef and node.parent.type !=
            symbols.decorated or node.type == symbols.decorated or node.type
            == symbols.simple_stmt):
            return True
        return False

    def transform(self, node, results):
        # Sometimes newlines are in prefix of current node, sometimes they're
        # in prefix of the prev sibling
        if node.prefix.count(u'\n'):
            newline_node = node
        else:
            newline_node = get_whitespace_before_definition(node)
            if not newline_node:
                # No previous node, must be the first node.
                return

        if newline_node.type in [token.INDENT, token.NEWLINE]:
            # If the newline_node is an indent or newline, we don't need to
            # worry about fixing indentation since it is not part of the
            # prefix. Dedents do have it as part of the prefix.
            curr_node_indentation = u''
        else:
            curr_node_indentation = find_indentation(node)
        min_lines_between_defs, max_lines_between_defs = (self.
            get_newline_limits(node))
        new_prefix = self.trim_comments(curr_node_indentation, newline_node.
            prefix, min_lines_between_defs, max_lines_between_defs)

        if newline_node.prefix != new_prefix:
            newline_node.prefix = new_prefix
            newline_node.changed()

    def get_newline_limits(self, node):
        if node.type == symbols.simple_stmt or has_parent(node, symbols.
            simple_stmt):
            max_lines_between_defs = 1
            min_lines_between_defs = 0
        elif has_parent(node, symbols.classdef) or has_parent(node, symbols.
            funcdef):
            # If we're inside a definition, only use a single space
            max_lines_between_defs = 1
            min_lines_between_defs = 1
        else:
            # Top-level definition
            max_lines_between_defs = 2
            min_lines_between_defs = 2
        return (min_lines_between_defs, max_lines_between_defs)

    def trim_comments(self, curr_node_indentation, previous_whitespace,
        min_lines_between_defs, max_lines_between_defs):
        before_comments, comments, after_comments = tuplize_comments(
            previous_whitespace)

        if before_comments.count(u"\n") > max_lines_between_defs:
            before_comments = u'\n' * max_lines_between_defs
        if after_comments.count(u"\n") > max_lines_between_defs:
            after_comments = u'\n' * max_lines_between_defs

        if (before_comments.count(u"\n") + after_comments.count(u"\n") >
            max_lines_between_defs):
            if before_comments and after_comments:
                # If there are spaces before and after, trim them down on both
                # sides to either 1 before and 1 after or 0 before and 1 after.
                before_comments = (u'\n' * (min_lines_between_defs - 1) if
                    min_lines_between_defs else u'')
                after_comments = u'\n'

        comment_lines = before_comments.count(u"\n") + after_comments.count(
            u"\n")
        if comment_lines < min_lines_between_defs:
            before_comments += (min_lines_between_defs - comment_lines) * u'\n'
        result = u'%s%s%s' % (before_comments, comments, after_comments)

        # Make sure that the result indenation matches the original indentation
        if result.split(u'\n')[-1] != curr_node_indentation:
            result = u"%s%s" % (result.rstrip(u' '), curr_node_indentation)
        return result
