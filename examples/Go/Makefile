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

CLI_GEN_FLAGS = --with_csv_parse --package=config --go_fmt
CLI_OUT_CSV_FLAGS = --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)
CLI_OUT_JSON_FLAGS = --out_data_format=json --json_indent --out_data_path=$(OUT_DATA_DIR)

all: output-csv output-json build run clean

generate:
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx $(CLI_GEN_FLAGS) --go_out=$(OUT_SRC_DIR)/soldier_define.go

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx $(CLI_GEN_FLAGS) --go_out=$(OUT_SRC_DIR)/guide_define.go

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx $(CLI_GEN_FLAGS) --go_out=$(OUT_SRC_DIR)/global_define.go

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx $(CLI_GEN_FLAGS) --go_out=$(OUT_SRC_DIR)/box_define.go

output:
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx $(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx $(CLI_OUT_JSON_FLAGS)

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx $(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx $(CLI_OUT_JSON_FLAGS)

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx $(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx $(CLI_OUT_JSON_FLAGS)

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx $(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx $(CLI_OUT_JSON_FLAGS)

run:
	GO111MODULE=off
	cd src && go test -v .
