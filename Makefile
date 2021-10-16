# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


all: run install upload

# run all examples
run:
	cd examples/Cpp && ${MAKE}
	cd examples/CSharp && ${MAKE}
	cd examples/Go && ${MAKE}
	cd examples/Java && ${MAKE}

# build distribute binary
install:
	pip install -r requirements.txt
	pyinstaller -F --name=tabugen tabugen/cli.py

# upload to pip
upload:
	python setup.py check && python setup.py bdist_wheel --universal && twine upload dist/*

clean:
	rm -rf build dist

.PHONEY: clean run install upload