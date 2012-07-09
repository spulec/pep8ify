#!/usr/bin/env python

from lib2to3.main import main

try:
    import pep8ify.fixes
except ImportError:
    # if importing pep8ify fails, try to load from parent
    # directory to support running without installation
    import imp, os
    if not hasattr(os, 'getuid') or os.getuid() != 0:
        imp.load_module('pep8ify', *imp.find_module('pep8ify',
            [os.path.dirname(os.path.dirname(__file__))]))


def _main():
    raise SystemExit(main("pep8ify.fixes"))

if __name__ == '__main__':
    _main()
