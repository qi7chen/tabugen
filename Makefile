# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


all: dist

dist:
	pip install -r requirements.txt
	pyinstaller -F --name=tabular tabular/cli.py

run_examples: