# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

rootDir = $(shell realpath ../../../)
currentDir = $(shell pwd)
dataDir = $(shell realpath ../../datasheet)

export PYTHONPATH=$(rootDir)

cli_entry = python $(rootDir)/tabular/cli.py
filepath = $(dataDir)/随机宝箱.xlsx

OUT_SRC_DIR = $(currentDir)/src/AutogenConfig
OUT_DATA_DIR = $(currentDir)/res


all: clean run

clean:
	rm -rf build
	rm -f res/*

run: build
	build/CppExample4 res

build: output
	mkdir -p build && cd build && cmake $(currentDir) && cmake --build $(currentDir)/build

output:
	$(cli_entry) --parse_files=$(filepath) --enable_column_skip --gen_csv_parse --source_file_encoding=gbk --cpp_out=$(OUT_SRC_DIR) --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)


