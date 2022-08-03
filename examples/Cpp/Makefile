# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

CURRENT_DIR = $(shell pwd)
ROOT_DIR = $(shell realpath ../../)
DATASHEET_DIR = $(shell realpath ../datasheet)
OUT_SRC_DIR = $(CURRENT_DIR)/src
OUT_DATA_DIR = $(DATASHEET_DIR)/res


export PYTHONPATH=$(ROOT_DIR)

TABUGEN_CLI = python $(ROOT_DIR)/tabugen/__main__.py

CLI_GEN_FLAGS = --with_csv_parse --package=config --source_file_encoding=utf_8_sig
CLI_OUT_CSV_FLAGS = --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

all: output build

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

run:
	mkdir -p cmake-build && cd cmake-build && cmake ..
	cmake --build $(CURRENT_DIR)/cmake-build && cmake-build/CppExample
