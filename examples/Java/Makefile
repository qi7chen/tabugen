# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.



CURRENT_DIR = $(shell pwd)
ROOT_DIR = $(shell realpath ../../../)
DATASHEET_DIR = $(shell realpath ../../datasheet)
OUT_SRC_DIR = $(CURRENT_DIR)/src
OUT_DATA_DIR = $(CURRENT_DIR)/res

export PYTHONPATH=$(ROOT_DIR)

TABUGEN_CLI = python $(ROOT_DIR)/tabugen/__main__.py

all: output-csv output-json build run clean

output:
	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/兵种.xlsx --gen_csv_parse --skip_column=Volume,Hurt --package=config \
		--go_out=$(OUT_SRC_DIR)/soldier_csv.go --go_fmt --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/兵种.xlsx --go_json_tag --skip_column=Volume,Hurt --package=config \
		--go_out=$(OUT_SRC_DIR)/soldier_json.go --go_fmt --out_data_format=json --json_indent --json_snake_case --out_data_path=$(OUT_DATA_DIR)

.PHONEY: clean run output-csv output-json