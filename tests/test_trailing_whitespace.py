#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil

from lib2to3.main import main

FIXTURE_PATH = './tests/fixtures/'


def setup():
    pass


def teardown():
    backup_filenames = [os.path.join(FIXTURE_PATH, filename) for filename in
                        os.listdir(FIXTURE_PATH) if filename.endswith(".bak")]
    for backup_filename in backup_filenames:
        shutil.move(backup_filename, backup_filename.replace(".bak", ""))


def test_all_fixtures():
    fixture_files = os.listdir(FIXTURE_PATH)
    fixture_in_files = [os.path.join(FIXTURE_PATH, fixture_file)
        for fixture_file in fixture_files if fixture_file.endswith("_in.py")]
    
    all_fixture_files = [(fixture_in, fixture_in.replace("_in.py", "_out.py"))
        for fixture_in in fixture_in_files]
    
    for in_file, out_file in all_fixture_files:
        yield check_fixture, in_file, out_file

test_all_fixtures.setup = setup
test_all_fixtures.teardown = teardown


def check_fixture(in_file, out_file):
    # filename = in_file.split("/")[-1]
    # fixer_name = filename.split(".")[0]
    # main("pep8ifier.fixes", args=['--fix', fixer_name, '-w', in_file])
    
    main("pep8ifier.fixes", args=['-w', in_file])
    assert (open(in_file).readlines() == open(out_file).readlines(),
                "Failure with %s" % in_file.split("/")[-1])
