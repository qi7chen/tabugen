#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

setup(
    name='tabugen',
    version='0.5.0',
    license='Apache',
    author='cheadaq',
    author_email='ichenq@outlook.com',
    url='https://github.com/cheadaq/tabugen',
    description=u'a table export and code generate tool for rapid game development',
    packages=find_packages(),
    install_requires=[
        'et-xmlfile>=1.0.1',
        'jdcal>=1.4.1',
        'openpyxl>=2.6.3',
        'PyMySQL>=0.9.3',
    ],
)