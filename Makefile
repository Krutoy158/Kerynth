PYTHON ?= python3

.PHONY: check test fetch

check:
	$(PYTHON) tools/kerynth-build check

test:
	$(PYTHON) -m unittest discover -s tests -v

fetch:
	$(PYTHON) tools/kerynth-build fetch
