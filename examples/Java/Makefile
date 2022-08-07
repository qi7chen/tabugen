# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

CURRENT_DIR = $(shell pwd)
ROOT_DIR = $(shell realpath ../../)
DATASHEET_DIR = $(shell realpath ../datasheet)
OUT_SRC_DIR = $(CURRENT_DIR)/src/main/java
OUT_DATA_DIR = $(DATASHEET_DIR)/res

export PYTHONPATH=$(ROOT_DIR)

TABUGEN_CLI = python $(ROOT_DIR)/tabugen/__main__.py
CLI_GEN_FLAGS =  --with_csv_parse --package=com.pdfun.config
CLI_OUT_CSV_FLAGS = --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)
CLI_OUT_JSON_FLAGS = --out_data_format=json --json_indent --out_data_path=$(OUT_DATA_DIR)

all: build clean

generate:
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx $(CLI_GEN_FLAGS) --java_out=$(OUT_SRC_DIR)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx $(CLI_GEN_FLAGS) --java_out=$(OUT_SRC_DIR)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx $(CLI_GEN_FLAGS) --java_out=$(OUT_SRC_DIR)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx $(CLI_GEN_FLAGS) --java_out=$(OUT_SRC_DIR)

output:
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx	$(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx	$(CLI_OUT_JSON_FLAGS)

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx	$(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx	$(CLI_OUT_JSON_FLAGS)

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx	$(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx	$(CLI_OUT_JSON_FLAGS)

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx	$(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx	$(CLI_OUT_JSON_FLAGS)

clean:
	mvn clean

run: build
	mvn exec:java -Dexec.mainClass="Sample"

build:
	mvn compile

.PHONEY: clean run generate output
