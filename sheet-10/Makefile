TEST_CMD = python3 -m doctest
CHECKSTYLE_CMD = flake8

all: compile test checkstyle

compile:
	@echo "Nothing to compile for Python"

test:
	$(TEST_CMD) *.py

checkstyle:
	$(CHECKSTYLE_CMD) *.py

start:
	python3 *.py example_train.txt example_test.txt

clean:
	rm -f *.pyc
	rm -rf __pycache__
