
VCPKG_DIR = $(HOME)/vcpkg

CURRENT_DIR = $(shell pwd)
ROOT_DIR = $(shell realpath ../../../)
DATASHEET_DIR = $(shell realpath ../../datasheet)

export PYTHONPATH=$(ROOT_DIR)

TABUGEN_CLI = python $(ROOT_DIR)/tabugen/cli.py

install_vcpkg: $(VCPKG_DIR)/vcpkg
	$(VCPKG_DIR)/vcpkg install abseil
	
$(VCPKG_DIR)/vcpkg:
	git clone https://github.com/microsoft/vcpkg $(VCPKG_DIR)
	sh $(VCPKG_DIR)/bootstrap-vcpkg.sh