PYTHON ?= python3

.PHONY: check test fetch

check:
	$(PYTHON) tools/aether-build check

test:
	$(PYTHON) -m unittest discover -s tests -v

fetch:
	$(PYTHON) tools/aether-build fetch
