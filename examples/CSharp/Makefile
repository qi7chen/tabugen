# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

CURRENT_DIR = $(shell pwd)
ROOT_DIR = $(shell realpath ../../)
DATASHEET_DIR = $(shell realpath ../datasheet)
OUT_DATA_DIR = $(CURRENT_DIR)/res

export PYTHONPATH=$(ROOT_DIR)

TABUGEN_CLI = python $(ROOT_DIR)/tabugen/__main__.py

all: output run

output:
	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/兵种.xlsx --gen_csv_parse  --package=Config --csharp_out=$(CURRENT_DIR)/basic/AutoConfig.cs \
		--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)
	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/兵种.xlsx --package=Config2 --csharp_out=$(CURRENT_DIR)/basic/AutoJsonConfig.cs \
		--out_data_format=json --json_indent --out_data_path=$(OUT_DATA_DIR)

	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/新手任务.xlsx --gen_csv_parse  --package=Config --csharp_out=$(CURRENT_DIR)/array-map/AutoConfig.cs \
		--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)
	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/新手任务.xlsx   --package=Config2 --csharp_out=$(CURRENT_DIR)/array-map/AutoJsonConfig.cs \
		--out_data_format=json --json_indent --out_data_path=$(OUT_DATA_DIR)

	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/全局变量表.xlsx --gen_csv_parse  --package=Config --csharp_out=$(CURRENT_DIR)/global-var/AutoConfig.cs \
		--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)
	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/全局变量表.xlsx --package=Config2 --csharp_out=$(CURRENT_DIR)/global-var/AutoJsonConfig.cs \
		--out_data_format=json --json_indent --out_data_path=$(OUT_DATA_DIR)

	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/随机宝箱.xlsx --gen_csv_parse  --package=Config --csharp_out=$(CURRENT_DIR)/inner-class/AutoConfig.cs \
		--out_data_format=csv --out_data_path=$(OUT_DATA_DIR)
	$(TABUGEN_CLI) --parse_files=$(DATASHEET_DIR)/随机宝箱.xlsx --package=Config2 --csharp_out=$(CURRENT_DIR)/inner-class/AutoJsonConfig.cs \
		--out_data_format=json --json_indent --out_data_path=$(OUT_DATA_DIR)

run:
	cd $(CURRENT_DIR)/basic && dotnet run

go:
	cd $(CURRENT_DIR)/array-map && dotnet run
	cd $(CURRENT_DIR)/global-var && dotnet run
	cd $(CURRENT_DIR)/inner-class && dotnet run


.PHONEY:
	clean build run