#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages
import os
import sys

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(this_directory)

with open(os.path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    readme = f.read()

tabugen_version = '0.6.7'

install_requires = [
    'et-xmlfile>=1.0.1',
    'jdcal>=1.4.1',
    'openpyxl>=2.6.3',
    'PyMySQL>=0.9.3',
]

setup(
    name='tabugen',
    version=tabugen_version,
    license='Apache License 2.0',
    author='cheadaq',
    author_email='ichenq@outlook.com',
    url='https://github.com/cheadaq/tabugen',
    description=u'a table export and code generate tool for rapid game development',
    long_description=readme,
    long_description_content_type='text/x-rst',
    python_requires='>=3.6',
    include_package_data=True,
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            "tabugen = tabugen.cli:main"
        ]
    }
)