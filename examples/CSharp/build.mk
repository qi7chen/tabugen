
CURRENT_DIR = $(shell pwd)
ROOT_DIR = $(shell realpath ../../../)
DATASHEET_DIR = $(shell realpath ../../datasheet)

export PYTHONPATH=$(ROOT_DIR)

TABUGEN_CLI = python $(ROOT_DIR)/tabugen/cli.py

all: output-csv output-json run clean
