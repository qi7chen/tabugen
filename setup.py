#!/usr/bin/env python
# coding: utf-8

import setuptools
import os
import sys

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(this_directory)

readme = open(os.path.join(this_directory, 'README.md'), 'r', encoding='utf-8').read()

tabugen_version = '1.1.0'

setuptools.setup(
    name='tabugen',
    version=tabugen_version,
    license='Apache License 2.0',
    author='Johnnie Chen',
    author_email='ichenq@outlook.com',
    url='https://github.com/ki7chen/tabugen',
    description=u'a spreadsheet export and code generation tool for rapid game development',
    long_description=readme,
    long_description_content_type='text/markdown',
    python_requires='>=3.9',
    include_package_data=True,
    packages=setuptools.find_packages(),
    install_requires=[
        'xlrd>=2.0.1',
        'openpyxl>=3.1.3',
        'inflect>=7.2.0',
    ],
    entry_points={
        'console_scripts': [
            "tabugen = tabugen.__main__:main"
        ]
    }
)
