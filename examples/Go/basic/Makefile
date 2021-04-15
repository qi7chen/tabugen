# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

rootDir = $(shell realpath ../../../)
currentDir = $(shell pwd)
dataDir = $(shell realpath ../../datasheet)

export PYTHONPATH=$(rootDir)

cli_entry = python $(rootDir)/tabugen/cli.py
filepath = $(dataDir)/兵种.xlsx

OUT_SRC_DIR = $(currentDir)/src
OUT_DATA_DIR = $(currentDir)/res


all: run clean

clean:

run: output-csv output-json
	cd src/csv && go test -v .
	cd src/json && go test -v .

output-csv:
	rm -f $(OUT_DATA_DIR)/*.csv
	$(cli_entry) --parse_files=$(filepath) --gen_csv_parse --skip_column=Volume,Hurt --package=config \
		--go_out=$(OUT_SRC_DIR)/csv/autoconfig.go --go_fmt --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

output-json:
	rm -f $(OUT_DATA_DIR)/*.json
	$(cli_entry) --parse_files=$(filepath) --go_json_tag --skip_column=Volume,Hurt --package=config \
		--go_out=$(OUT_SRC_DIR)/json/autoconfig.go --go_fmt --out_data_format=json --json_indent --json_snake_case --out_data_path=$(OUT_DATA_DIR)

.PHONEY: clean run output-csv output-json