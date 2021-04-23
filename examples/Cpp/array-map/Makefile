# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


include ../build.mk

FILE_PATH = $(DATASHEET_DIR)/新手任务.xlsx

OUT_SRC_DIR = $(CURRENT_DIR)/src/AutogenConfig
OUT_DATA_DIR = $(CURRENT_DIR)/res


clean:
	rm -rf build
	rm -f $(OUT_DATA_DIR)/newbie_guide_define.csv

run: build/bin/CppExample3
	build/bin/CppExample3 res

build: install_vcpkg $(OUT_DATA_DIR)/newbie_guide_define.csv
	mkdir -p build && cd build && \
	cmake $(CURRENT_DIR) && cmake --build $(CURRENT_DIR)/build

$(OUT_DATA_DIR)/newbie_guide_define.csv: 
	$(TABUGEN_CLI) --parse_files=$(FILE_PATH) --gen_csv_parse --cpp_out=$(OUT_SRC_DIR) \
		--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

.PHONEY: clean build run output