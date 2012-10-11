BINARY_OPERATORS = frozenset(['**=', '*=', '+=', '-=', '!=', '<>',
    '%=', '^=', '&=', '|='])

a = range(10)
b = range(5)
foo = [a, b]
bar = (3,)
bar = (3, 1,)
foo = [1,2,]
foo = [1, 3]

foobar = a[1:4]
foobar = a[:4]
foobar = a[1:]
foobar = a[1:4:2]

foobar = ['a','b']
foobar = foo(bar,baz)


def tester_func():
    if node_to_split.type in [symbols.or_test, symbols.and_test, symbols.
        not_test, symbols.test, symbols.arith_expr, symbols.comparison]:
        pass
