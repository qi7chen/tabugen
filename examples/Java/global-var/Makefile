# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

rootDir = $(shell realpath ../../../)
currentDir = $(shell pwd)
dataDir = $(shell realpath ../../datasheet)

export PYTHONPATH=$(rootDir)

cli_entry = python $(rootDir)/tabugen/cli.py
filepath = $(dataDir)/全局变量表.xlsx

OUT_SRC_DIR = $(currentDir)/src/main/java
OUT_DATA_DIR = $(currentDir)/res
PKG1_NAME = com.mycompany.csvconfig
PKG2_NAME = com.mycompany.jsonconfig

all: clean run

clean:
	rm -f res/*
	mvn clean

run: build
	mvn exec:java -Dexec.mainClass="Sample"

build: output-csv output-json
	mvn compile

output-csv:
	$(cli_entry) --parse_files=$(filepath) --gen_csv_parse --package=$(PKG1_NAME) --java_out=$(OUT_SRC_DIR) --out_data_format=csv --out_data_path=$(OUT_DATA_DIR)

output-json:
	$(cli_entry) --parse_files=$(filepath) --go_json_tag --package=$(PKG2_NAME) --java_out=$(OUT_SRC_DIR) --out_data_format=json --json_indent --out_data_path=$(OUT_DATA_DIR)
