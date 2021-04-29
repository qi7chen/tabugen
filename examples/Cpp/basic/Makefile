# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

include ../build.mk

FILE_PATH = $(DATASHEET_DIR)/兵种.xlsx

OUT_SRC_DIR = $(CURRENT_DIR)/src/AutogenConfig
OUT_DATA_DIR = $(CURRENT_DIR)/res


clean:
	rm -rf build

run: build/bin/CppExample1
	build/bin/CppExample1 res

build/bin/CppExample1: build

build: install_abseil output
	mkdir -p build  && cd build && \
	cmake $(CURRENT_DIR) && cmake --build $(CURRENT_DIR)/build

output: 
	rm -f $(OUT_DATA_DIR)/*.csv
	$(TABUGEN_CLI) --parse_files=$(FILE_PATH) --skip_column=Volume,Hurt --gen_csv_parse \
		--cpp_out=$(OUT_SRC_DIR) --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)


.PHONY: clean build run output