# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

rootDir = $(shell realpath ../../../)
currentDir = $(shell pwd)
dataDir = $(shell realpath ../../datasheet)

export PYTHONPATH=$(rootDir)

cli_entry = python $(rootDir)/tabugen/cli.py
filepath = $(dataDir)/新手任务.xlsx

OUT_SRC_DIR = $(currentDir)/src
OUT_DATA_DIR = $(currentDir)/res


all: run clean

clean:
	rm -rf src/bin src/obj src/.vs

run: output-csv output-json
	cd src && dotnet run

output-csv:
	rm -f res/*.csv
	$(cli_entry) --parse_files=$(filepath) --gen_csv_parse --package=Config  --csharp_out=$(OUT_SRC_DIR)/AutoConfig.cs \
		--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

output-json:
	rm -f res/*.json
	$(cli_entry) --parse_files=$(filepath) --package=Config2  --csharp_out=$(OUT_SRC_DIR)/AutoJsonConfig.cs \
		--out_data_format=json --json_indent --out_data_path=$(OUT_DATA_DIR)

.PHONEY: clean build run output-csv output-json