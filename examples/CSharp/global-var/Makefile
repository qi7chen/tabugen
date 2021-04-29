# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

include ../build.mk

FILE_PATH = $(DATASHEET_DIR)/全局变量表.xlsx

OUT_SRC_DIR = $(CURRENT_DIR)/src
OUT_DATA_DIR = $(CURRENT_DIR)/res


clean:
	rm -rf src/bin src/obj src/.vs

run: output-csv output-json
	cd src && dotnet run

output-csv:
	rm -f $(OUT_DATA_DIR)/*.csv
	$(TABUGEN_CLI) --parse_files=$(FILE_PATH) --gen_csv_parse --package=Config  --csharp_out=$(OUT_SRC_DIR)/AutoConfig.cs \
		--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

output-json:
	rm -f $(OUT_DATA_DIR)/*.json
	$(TABUGEN_CLI) --parse_files=$(FILE_PATH) --package=Config2  --csharp_out=$(OUT_SRC_DIR)/AutoJsonConfig.cs \
		--out_data_format=json --json_indent --out_data_path=$(OUT_DATA_DIR)

.PHONEY: clean build run output-csv output-json