PYTHON ?= python3

.PHONY: check test fetch initramfs

check:
	$(PYTHON) tools/kerynth-build check

test:
	$(PYTHON) -m unittest discover -s tests -v

fetch:
	$(PYTHON) tools/kerynth-build fetch

initramfs:
	$(PYTHON) tools/kerynth-initramfs --root .kerynth-work/initramfs-root --output .kerynth-work/initramfs.cpio.gz
