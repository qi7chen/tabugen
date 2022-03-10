# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

CURRENT_DIR = $(shell pwd)
ROOT_DIR = $(shell realpath ../../)
DATASHEET_DIR = $(shell realpath ../datasheet)
OUT_DATA_DIR = $(CURRENT_DIR)/res

VCPKG_TOOLCHAIN_FILE ?= $(HOME)/vcpkg/scripts/buildsystems/vcpkg.cmake
VCPKG_INCLUDE_DIR_ ?= $(HOME)/vcpkg/installed/x64-linux/include
VCPKG_LIB_DIR_ = ?= $(HOME)/vcpkg/installed/x64-linux/lib

export PYTHONPATH=$(ROOT_DIR)
export VCPKG_INCLUDE_DIR=$(VCPKG_INCLUDE_DIR_)
export VCPKG_LIB_DIR=$(VCPKG_LIB_DIR_)

TABUGEN_CLI = python $(ROOT_DIR)/tabugen/cli.py

all: output build

install_vcpkg:
	cd $(HOME) && git clone https://github.com/microsoft/vcpkg 
	$(HOME)/vcpkg/bootstrap-vcpkg.sh
	$(HOME)/vcpkg/vcpkg install abseil

clean:
	rm -rf build

output:
	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/兵种.xlsx --gen_csv_parse --cpp_out=$(CURRENT_DIR)/basic/AutogenConfig \
		--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/新手任务.xlsx --gen_csv_parse --cpp_out=$(CURRENT_DIR)/array-map/AutogenConfig \
		--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/全局变量表.xlsx --gen_csv_parse --cpp_out=$(CURRENT_DIR)/global-var/AutogenConfig \
		--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/随机宝箱.xlsx --gen_csv_parse --cpp_out=$(CURRENT_DIR)/inner-class/AutogenConfig \
		--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)	
			
build:
	mkdir -p build && cd build && cmake -DCMAKE_TOOLCHAIN_FILE=$(VCPKG_TOOLCHAIN_FILE) .. 
	cmake --build $(CURRENT_DIR)/build
