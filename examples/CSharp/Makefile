# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

CURRENT_DIR = $(shell pwd)
ROOT_DIR = $(shell realpath ../../)
DATASHEET_DIR = $(shell realpath ../datasheet)
OUT_DATA_DIR = $(DATASHEET_DIR)/res

export PYTHONPATH=$(ROOT_DIR)

TABUGEN_CLI = python $(ROOT_DIR)/tabugen/__main__.py

CLI_GEN_FLAGS =   --package=Config
CLI_OUT_CSV_FLAGS = --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)
CLI_OUT_JSON_FLAGS = --out_data_format=json --json_indent --out_data_path=$(OUT_DATA_DIR)

all: output run

generate:
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx  $(CLI_GEN_FLAGS) --csharp_out=$(CURRENT_DIR)/src/SoldierDefine.cs
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx $(CLI_GEN_FLAGS) --csharp_out=$(CURRENT_DIR)/src/GuideDefine.cs
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx $(CLI_GEN_FLAGS) --csharp_out=$(CURRENT_DIR)/src/GlobalDefine.cs
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx $(CLI_GEN_FLAGS) --csharp_out=$(CURRENT_DIR)/src/BoxDefine.cs

output:
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx $(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/兵种.xlsx $(CLI_OUT_JSON_FLAGS)

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx $(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/新手任务.xlsx $(CLI_OUT_JSON_FLAGS)

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx $(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/全局变量表.xlsx $(CLI_OUT_JSON_FLAGS)

	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx $(CLI_OUT_CSV_FLAGS)
	$(TABUGEN_CLI) --asset_path=$(DATASHEET_DIR)/随机宝箱.xlsx $(CLI_OUT_JSON_FLAGS)

run:
	cd $(CURRENT_DIR)/src && dotnet run


.PHONEY:
	clean build run
