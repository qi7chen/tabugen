# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

CURRENT_DIR = $(shell pwd)
ROOT_DIR = $(shell realpath ../../)
DATASHEET_DIR = $(shell realpath ../datasheet)
OUT_SRC_DIR = $(CURRENT_DIR)/src
OUT_DATA_DIR = $(CURRENT_DIR)/res

export PYTHONPATH=$(ROOT_DIR)

TABUGEN_CLI = python $(ROOT_DIR)/tabugen/__main__.py

all: output-csv output-json build run clean

generate:
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx --go_json_tag --json_snake_case --enable_gen_csv_parse --package=config \
		--go_out=$(OUT_SRC_DIR)/soldier_define.go --go_fmt

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx --go_json_tag --json_snake_case --enable_gen_csv_parse --package=config \
		--go_out=$(OUT_SRC_DIR)/guide_define.go --go_fmt

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx --go_json_tag --json_snake_case --enable_gen_csv_parse --package=config \
		--go_out=$(OUT_SRC_DIR)/global_define.go --go_fmt

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx --go_json_tag  --json_snake_case --enable_gen_csv_parse --package=config \
		--go_out=$(OUT_SRC_DIR)/box_define.go --go_fmt

output:
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx	--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx	--out_data_format=json --json_indent --json_snake_case  --out_data_path=$(OUT_DATA_DIR)

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx	--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx	--out_data_format=json --json_indent --json_snake_case  --out_data_path=$(OUT_DATA_DIR)

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx	--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx	--out_data_format=json --json_indent --json_snake_case  --out_data_path=$(OUT_DATA_DIR)

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx	--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx	--out_data_format=json --json_indent --json_snake_case  --out_data_path=$(OUT_DATA_DIR)

run:
	GO111MODULE=off
	cd src && go mod init tabugen && go test -v .
