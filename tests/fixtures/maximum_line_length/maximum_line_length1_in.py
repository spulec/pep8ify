class tester:
    u"""this is testing the maximum length of a docstring and it is very long to ensure that the test will work well"""

    # This is a multiple line comment in front of a method that is defined inside of a class
    # and this is the second line
    def testering(self):
        print u"testering"

    # this is another testerig comment that makes sure that we are able to test the fixer properly.
    def tester2():
        u'''This is a long docstring that is inside of a function which is inside of a class'''
        return


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


def tester4():
    tester_object.test_a_really_long_method().chain_it_with_another_super_long_method_name()


def tester5():
    if (tester1 == tester2 and tester3 == tester4 and tester5 == tester6 and tester7 == tester8):
        print "good testing"


def tester_func(param1=u'param_value1', param2=u'param_value2', param3=u'param_value3', param4=u'param_value4'):
    print "good testing"

tester_func(param1=u'param_value1', param2=u'param_value2', param3=u'param_value3', param4=u'param_value4')
