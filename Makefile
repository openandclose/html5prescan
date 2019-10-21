PHONIES = all test flake8 git


all: test tox flake8 git

.PHONY: $(PHONIES)


test:
	python -m doctest src/html5prescan/replacement.py
	python test/test_data.py

tox:
	tox

flake8:
	flake8 .

git:
	git update-index --refresh
	git diff-index --quiet HEAD --
