class tester(object):
    def __init__(self, attr1, attr2): 
        self.attr1 = attr1
        self.attr2 = attr2 
        self.attr3 = ["one string", 
            "another string"]
    
    def __unicode__(self):
        return u"testing unicode response"
    
    def test_method(self):
        return self.attr1 + self.attr2
    
    def test_method2(self, suffix):
        return "%s %s" % (self.attr1, suffix) 
    
    # This is a comment 
    # This is another comment 
    def test_method3(self):
        print("testing this %s", self.attr2)
