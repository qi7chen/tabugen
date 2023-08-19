#!/usr/bin/env python
# coding: utf-8

import setuptools
import os
import sys

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(this_directory)

with open(os.path.join(this_directory, 'README.md'), 'r', encoding='utf-8') as fh:
    readme = fh.read()

tabugen_version = '1.0.1'

install_requires = [
    'xlrd>=2.0.1',
    'openpyxl>=3.1.2',
]

setuptools.setup(
    name='tabugen',
    version=tabugen_version,
    license='Apache License 2.0',
    author='JohnnieChen',
    author_email='ichenq@outlook.com',
    url='https://github.com/qki7chen/tabugen',
    description=u'a spreedsheet export and code generate tool for rapid game development',
    long_description=readme,
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
    include_package_data=True,
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            "tabugen = tabugen.__main__:main"
        ]
    }
)
