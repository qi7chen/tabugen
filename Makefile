# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


all: install upload

# build distribute binary
install:
	@pip install -r requirements.txt
	@pyinstaller -F --name=tabugen tabugen/cli.py

# upload to pip
upload:
	@python setup.py check && python setup.py bdist_wheel --universal && twine upload dist/*

clean:
	@python -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
	@python -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"
	@rm -rf build dist

.PHONEY: clean run install upload
