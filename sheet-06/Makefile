FILE = wikidata-entities.tsv
PORT = 8081
all: compile test checkstyle

compile:
	python3 -m py_compile *.py

test:
	python3 -m doctest *.py

checkstyle:
	flake8 *.py

clean:
	rm -rf __pycache__
	rm -f *.pyc

start:
	python3 search_server.py $(FILE) $(PORT)
