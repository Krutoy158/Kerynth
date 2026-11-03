PYTHON ?= python3

.PHONY: check test fetch rootfs kernel initramfs iso-stage hardware iso-check iso build

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

hardware:
	$(PYTHON) tools/kerynth-hw --json

iso-check:
	$(PYTHON) tools/kerynth-iso check

iso:
	$(PYTHON) tools/kerynth-iso build

build:
	$(PYTHON) tools/kerynth-build-pipeline build
