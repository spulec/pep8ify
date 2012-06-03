SHELL := /bin/bash

init:
	python setup.py develop
	pip install -r requirements.txt

test:
	nosetests --with-color ./tests/

tdaemon:
	tdaemon -t nose ./tests/ --custom-args="--with-growl"
