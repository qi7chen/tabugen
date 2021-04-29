# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

include ../build.mk

FILE_PATH = $(DATASHEET_DIR)/新手任务.xlsx

OUT_SRC_DIR = $(CURRENT_DIR)/src/main/java
OUT_DATA_DIR = $(CURRENT_DIR)/src/main/resources

PKG1_NAME = com.pdfun.csvconfig
PKG2_NAME = com.pdfun.jsonconfig


clean:
	mvn clean

run: build
	mvn exec:java -Dexec.mainClass="Sample"

build: output-csv output-json
	mvn compile

output-csv:
	rm -f $(OUT_DATA_DIR)/*.csv
	$(TABUGEN_CLI) --parse_files=$(FILE_PATH) --gen_csv_parse --package=$(PKG1_NAME) --java_out=$(OUT_SRC_DIR) --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

output-json:
	rm -f $(OUT_DATA_DIR)/*.json
	$(TABUGEN_CLI) --parse_files=$(FILE_PATH) --go_json_tag --package=$(PKG2_NAME) --java_out=$(OUT_SRC_DIR) --out_data_format=json --json_indent --out_data_path=$(OUT_DATA_DIR)

.PHONEY: clean build run output-csv output-json