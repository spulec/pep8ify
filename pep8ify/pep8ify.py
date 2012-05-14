#!/usr/bin/env python

from os.path import abspath, dirname, join
import sys

from lib2to3.main import main

sys.path.insert(0, abspath(join(dirname(__file__), u"../")))

sys.exit(main("pep8ify.fixes"))
