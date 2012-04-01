from lib2to3.fixer_base import BaseFix
from lib2to3.pgen2 import token


class FixWhitespaceBeforeInlineComment(BaseFix):
    u''' Separate inline comments by at least two spaces.

    An inline comment is a comment on the same line as a statement.  Inline
    comments should be separated by at least two spaces from the statement.
    They should start with a # and a single space.

    '''
    
    _accept_type = token.NEWLINE
    
    def match(self, node):
        position = node.prefix.find(u"#")
        if -1 < position:# < 2 or node.prefix[position + 1] != u" ":
            return True
        return False
    
    def transform(self, node, results):
        position = node.prefix.find(u"#")
        if position > 2:
            whitespace_before, comment_after = node.prefix.split(u"#", 1)
            node.prefix = u"%s# %s" % (whitespace_before, comment_after.lstrip())
        else:
            node.prefix = u"  # %s" % node.prefix.replace(u"#", u"", 1).lstrip()
        node.changed()
