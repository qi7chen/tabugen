# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

include ../build.mk

FILE_PATH = $(DATASHEET_DIR)/新手任务.xlsx

OUT_SRC_DIR = $(CURRENT_DIR)/src
OUT_DATA_DIR = $(CURRENT_DIR)/res


clean:
	
run: output-csv output-json
	cd src/csv && GO111MODULE=off go test -v .
	cd src/json && GO111MODULE=off go test -v .

output-csv:
	rm -f $(OUT_DATA_DIR)/*.csv
	$(TABUGEN_CLI) --parse_files=$(FILE_PATH) --gen_csv_parse --package=config --go_out=$(OUT_SRC_DIR)/csv/autoconfig.go \
		--go_fmt --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

output-json:
	rm -f $(OUT_DATA_DIR)/*.json
	$(TABUGEN_CLI) --parse_files=$(FILE_PATH) --go_json_tag --package=config --go_out=$(OUT_SRC_DIR)/json/autoconfig.go \
		--go_fmt --out_data_format=json --json_indent --json_snake_case --out_data_path=$(OUT_DATA_DIR)

.PHONEY: clean run output-csv output-json