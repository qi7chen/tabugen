# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

from taksi.parser.excel import ExcelStructParser
from taksi.parser.mysql import MySQLStructParser

from taksi.generator.cpp.gen_struct import CppStructGenerator
from taksi.generator.csharp.gen_struct import CSharpStructGenerator

from taksi.datatran.csv import CsvDataWriter
from taksi.datatran.json import JsonDataWriter

# 结构体描述解析
struct_parser_registry = {
    ExcelStructParser.name(): ExcelStructParser(),
    MySQLStructParser.name(): MySQLStructParser(),
}

# 源代码生成
code_generator_registry = {
    CppStructGenerator.name(): CppStructGenerator(),
    CSharpStructGenerator.name(): CSharpStructGenerator,
}

# 数据文件写入
data_writer_registry = {
    CsvDataWriter.name(): CsvDataWriter(),
    JsonDataWriter.name(): JsonDataWriter(),
}


#
def get_struct_parser(name):
    return struct_parser_registry.get(name, None)


#
def get_code_generator(name):
    return code_generator_registry.get(name, None)


#
def get_data_writer(name):
    return data_writer_registry.get(name, None)
