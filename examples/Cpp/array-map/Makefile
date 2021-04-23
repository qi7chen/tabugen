# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


include ../build.mk

FILE_PATH = $(DATASHEET_DIR)/新手任务.xlsx

OUT_SRC_DIR = $(CURRENT_DIR)/src/AutogenConfig
OUT_DATA_DIR = $(CURRENT_DIR)/res

all: run clean

clean:
	rm -rf build

run: build
	build/CppExample3 res

build: install_vcpkg output
	mkdir -p build && cd build && \
	cmake $(CURRENT_DIR) -DCMAKE_TOOLCHAIN_FILE=$(VCPKG_DIR)/scripts/buildsystems/vcpkg.cmake && cmake --build $(CURRENT_DIR)/build

output: 
	rm -f $(OUT_DATA_DIR)/*.csv
	$(TABUGEN_CLI) --parse_files=$(FILE_PATH) --gen_csv_parse --cpp_out=$(OUT_SRC_DIR) \
		--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

.PHONEY: clean build run output