#!/usr/bin/env python

from setuptools import setup
import pep8ify

setup(
    name="pep8ify",
    license='Apache License 2.0',
    version=pep8ify.__version__,
    description="Cleans your python code to conform to pep8",
    author="Steve Pulec",
    author_email="spulec@gmail.com",
    url="https://github.com/spulec/pep8ify",
    packages=["pep8ify", "pep8ify.fixes"],
    entry_points={
        'console_scripts': [
            'pep8ify = pep8ify.pep8ify:_main',
        ],
    },
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ])
