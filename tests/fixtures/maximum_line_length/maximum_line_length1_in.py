testing = tuplize_comments("this is a short string")  # This is an inline comment that goes over 79 chars
testing = tuplize_comments("this is a longer string that breaks the 79 char limit")  # This is an inline comment that goes over 79 chars

LSTRIP_TOKENS = ["foobar1", "foobar1", "foobar1", "foobar1", "foobar1", "foo23", "foobar1", "foobar1"]

if ("foobar" == "foobar" or "foobar" == "foobar" or "foobar" == "foobar" or "foobar2" == "foobar"
    or "foobar" == "foobar" or "foobar" == "foobar" or "foobar" == "foobar" or "foobar3" == "foobar"):
    pass
new_prefix = '\n'.join([u"%s%s" % ("new_comment_indent", line.lstrip()) if line else u'' for line in "new_prefix".split('\n')]).rstrip(u' ') + "another long string"
from .utils import get_whitespace_before_definition, has_parent, tuplize_comments
before_comments, comments, after_comments_and_this_string_goes_on = tuplize_comments(u"asjdfsjf js ffsadasdfsf")

# Comment 1
new_prefix = ('\n'.join([u"%s%s" % (new_comment_indent, line.lstrip()) if line else u'' for  # A Comment
    line in new_prefix.split('\n')]).rstrip(u' '))


class tester:
    u"""this is testing the maximum length of a docstring and it is very long to ensure that the test will work well"""

    # This is a multiple line comment in front of a method that is defined inside of a class
    # and this is the second line
    def testering(self):
        print u"testering"
    
    # this is another testerig comment that makes sure that we are able to test the fixer properly.
    def tester2():
        u'''This is a long docstring that is inside of a function which is inside of a class'''
        new_comment_indent = u''
        new_prefix = u''
        # Split the lines of comment and prepend them with the new indent value
        if True:
            new_prefix = '\n'.join([u"%s%s" % (new_comment_indent, line.lstrip()) if line else u'' for line in new_prefix.split('\n')]).rstrip(u' ')
        # Allow unary operators: -123, -x, +1.
        if node.value in UNARY_OPERATORS and node.parent.type == symbols.factor:
            pass
        comment_start = 2
        comments = u''
        prefix = u''
        return prefix[:comments_start].strip(u' '), comments, prefix[comments_start + len(comments):]


# This is a tester comment that ensures we are able to fix top-level comments to not be too long.
def tester6():
    u'this is a single quoted docstring. I don\'t like them, but some people still use them'

    tester9 = u"all lines over 80 chars"
    # If someone uses string concat like this, I'm pretty sure the interpreter punches them in the face, but we should fix it anyway
    print "this is going to be" + "test that ensures that" + tester9 + "will be fixed appropriately"
    print "%s%s" % (tester9, "and another string that will make the total length go over 80s")

the_fixering = "testing"
that_other_thing_that_makes_this_over_eighty_chars_total = "testing2"
testering = the_fixering + that_other_thing_that_makes_this_over_eighty_chars_total


def tuplize_comments(prefix):
    prefix = "foo"
    if prefix.count("#"):
        pass
    else:
        if prefix.count(u'\n'):
            comments = prefix.rsplit(u'\n')[1]  # If no comments, there are no comments except the trailing spaces before the current line
        else:
            comments = prefix
    comments_start = prefix.index(comments)

testing = tuplize_comments("this one string" + "another string that makes this line too long")


def tester4():
    # This is a docstring that starts with a '#' and is greater than the max chars

    tester_object.test_a_really_long_method().chain_it_with_another_super_long_method_name()


def tester5():
    if (tester1 == tester2 and tester3 == tester4 and tester5 == tester6 and tester7 == tester8):
        print "good testing"


def tester_func(param1=u'param_value1', param2=u'param_value2', param3=u'param_value3', param4=u'param_value4'):
    print "good testing"

tester_func(param1=u'param_value1', param2=u'param_value2', param3=u'param_value3', param4=u'param_value4')


def testing_func():
    if (node.type == symbols.funcdef and node.parent.type != symbols.decorated
        or node.type == symbols.classdef or node.type == symbols.decorated or node.type == symbols.simple_stmt):
        return node.type, node.type2, node.type3, node.type4, node.type5, node.type6
