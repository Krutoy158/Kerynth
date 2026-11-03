PYTHON ?= python3

.PHONY: check test fetch rootfs kernel initramfs iso-stage install-tree hardware iso-check iso build

check:
	$(PYTHON) tools/kerynth-build check

test:
	$(PYTHON) -m unittest discover -s tests -v

fetch:
	$(PYTHON) tools/kerynth-build fetch

rootfs:
	$(PYTHON) tools/kerynth-build-pipeline rootfs

kernel:
	$(PYTHON) tools/kerynth-build-pipeline kernel

initramfs:
	$(PYTHON) tools/kerynth-build-pipeline initramfs

iso-stage:
	$(PYTHON) tools/kerynth-build-pipeline iso-stage

install-tree:
	$(PYTHON) tools/kerynth-install-tree --target test-install --mode manual --root-uuid 12345678-1234-1234-1234-123456789abc --username kerynth --password-hash '$6$temporary$replace-this-hash-before-use'

hardware:
	$(PYTHON) tools/kerynth-hw --json

iso-check:
	$(PYTHON) tools/kerynth-iso check

iso:
	$(PYTHON) tools/kerynth-iso build

build:
	$(PYTHON) tools/kerynth-build-pipeline build
