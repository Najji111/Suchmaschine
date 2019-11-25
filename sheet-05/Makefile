all: compile test checkstyle

compile:
	cd ped_c && python3 setup.py install --user
	python3 -m py_compile *.py

test:
	python3 -m doctest *.py

checkstyle:
	flake8 *.py

clean:
	rm -rf __pycache__
	rm -f *.pyc
