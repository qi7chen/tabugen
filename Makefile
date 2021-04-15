# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


all: run install upload

# run all examples
run:
	cd examples/Cpp && make
	cd examples/CSharp && make
	cd examples/Go && make
	cd examples/Java && make

# build distribute binary
install:
	pip install -r requirements.txt
	pyinstaller -F --name=tabugen tabugen/cli.py

# upload to pip
upload:
	python setup.py check && python setup.py sdist upload

clean:
	rm -rf build dist

.PHONEY: clean run install upload