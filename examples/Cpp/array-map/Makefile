# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

rootDir = $(shell realpath ../../../)
currentDir = $(shell pwd)
dataDir = $(shell realpath ../../datasheet)

export PYTHONPATH=$(rootDir)

cli_entry = python $(rootDir)/tabugen/cli.py
filepath = $(dataDir)/新手任务.xlsx

OUT_SRC_DIR = $(currentDir)/src/AutogenConfig
OUT_DATA_DIR = $(currentDir)/res

all: run clean

clean:
	rm -rf build

run: build
	build/CppExample3 res

build: output
	mkdir -p build && cd build && cmake $(currentDir) && cmake --build $(currentDir)/build

output: 
	rm -f $(OUT_DATA_DIR)/*.csv
	$(cli_entry) --parse_files=$(filepath) --gen_csv_parse --cpp_out=$(OUT_SRC_DIR) \
		--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

.PHONEY: clean build run output