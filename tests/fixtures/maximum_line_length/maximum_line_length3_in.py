def tester():
    foo = 1 + 2
    if not foo:
        logger.error(u"This is a long logger message that goes over the max length: %s", foo)
