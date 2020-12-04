# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

from tabular.parser.excel import ExcelStructParser

from tabular.generator.cpp.gen_struct import CppStructGenerator
from tabular.generator.csharp.gen_struct import CSharpStructGenerator
from tabular.generator.go.gen_struct import GoStructGenerator
from tabular.generator.java.gen_struct import JavaStructGenerator

from tabular.datatran.csv import CsvDataWriter
from tabular.datatran.json import JsonDataWriter
from tabular.datatran.sql import SQLDataWriter

# 结构体描述解析
struct_parser_registry = {
    ExcelStructParser.name(): ExcelStructParser(),
}

# 源代码生成
code_generator_registry = {
    CppStructGenerator.name(): CppStructGenerator(),
    CSharpStructGenerator.name(): CSharpStructGenerator(),
    GoStructGenerator.name(): GoStructGenerator(),
    JavaStructGenerator.name(): JavaStructGenerator(),
}

# 数据文件写入
data_writer_registry = {
    CsvDataWriter.name(): CsvDataWriter(),
    JsonDataWriter.name(): JsonDataWriter(),
    SQLDataWriter.name(): SQLDataWriter(),
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
