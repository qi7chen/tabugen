# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

CURRENT_DIR = $(shell pwd)
ROOT_DIR = $(shell realpath ../../)
DATASHEET_DIR = $(shell realpath ../datasheet)
OUT_SRC_DIR = $(CURRENT_DIR)/src
OUT_DATA_DIR = $(DATASHEET_DIR)/res

VCPKG_TOOLCHAIN_FILE ?= $(HOME)/vcpkg/scripts/buildsystems/vcpkg.cmake
VCPKG_INCLUDE_DIR_ ?= $(HOME)/vcpkg/installed/x64-linux/include
VCPKG_LIB_DIR_ = ?= $(HOME)/vcpkg/installed/x64-linux/lib

export PYTHONPATH=$(ROOT_DIR)
export VCPKG_INCLUDE_DIR=$(VCPKG_INCLUDE_DIR_)
export VCPKG_LIB_DIR=$(VCPKG_LIB_DIR_)

TABUGEN_CLI = python $(ROOT_DIR)/tabugen/__main__.py

CLI_GEN_FLAGS = --enable_csv_parse --package=config --source_file_encoding=utf_8_sig
CLI_OUT_CSV_FLAGS = --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

all: output build

install_vcpkg:
	cd $(HOME) && git clone https://github.com/microsoft/vcpkg
	$(HOME)/vcpkg/bootstrap-vcpkg.sh
	$(HOME)/vcpkg/vcpkg install abseil

clean:
	rm -rf build

generate:
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx $(CLI_GEN_FLAGS) --cpp_out=$(OUT_SRC_DIR)/SoldierDefine
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx $(CLI_GEN_FLAGS) --cpp_out=$(OUT_SRC_DIR)/GuideDefine
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx $(CLI_GEN_FLAGS) --cpp_out=$(OUT_SRC_DIR)/GlobalDefine
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx $(CLI_GEN_FLAGS) --cpp_out=$(OUT_SRC_DIR)/BoxDefine

output:
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx $(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx $(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

build:
	mkdir -p cmake-build && cd cmake-build && cmake -DCMAKE_TOOLCHAIN_FILE=$(VCPKG_TOOLCHAIN_FILE) ..
	cmake --build $(CURRENT_DIR)/cmake-build
