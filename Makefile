
PYTHON = python
PANDOC = pandoc

EMAIL = "mahtin@mahtin.com"

all:	README.rst build

README.rst: README.md
	$(PANDOC) --from=markdown --to=rst < README.md > README.rst 

build: setup.py
	$(PYTHON) setup.py build

install: build
	sudo $(PYTHON) setup.py install

test: all
	# to be done

sdist: all
	make clean
	make test
	$(PYTHON) setup.py sdist

upload: clean all
	$(PYTHON) setup.py sdist upload --sign --identity="$(EMAIL)"

clean:
	rm -rf build dist
	$(PYTHON) setup.py clean

