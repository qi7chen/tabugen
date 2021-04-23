
VCPKG_DIR = $(HOME)/vcpkg

CURRENT_DIR = $(shell pwd)
ROOT_DIR = $(shell realpath ../../../)
DATASHEET_DIR = $(shell realpath ../../datasheet)

export PYTHONPATH=$(ROOT_DIR)

TABUGEN_CLI = python $(ROOT_DIR)/tabugen/cli.py

all: run clean

install_abseil: $(CURRENT_DIR)/build/conanbuildinfo.cmake
	cd $(CURRENT_DIR)/build && conan install $(CURRENT_DIR)/..
	
$(CURRENT_DIR)/build/conanbuildinfo.cmake:
	pip install conan
	mkdir -p $(CURRENT_DIR)/build && cd $(CURRENT_DIR)/build && conan install $(CURRENT_DIR)/..