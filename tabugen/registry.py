# Copyright (C) 2024 ki7chen@github. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

from tabugen.writer.csv import CsvDataWriter
from tabugen.writer.json import JsonDataWriter
from tabugen.generator.cpp.gen_struct import CppStructGenerator
# from tabugen.generator.csharp.gen_struct import CSharpStructGenerator
from tabugen.generator.go.gen_struct import GoStructGenerator
# from tabugen.generator.java.gen_struct import JavaStructGenerator
from tabugen.parser.sheet_parser import SpreadSheetParser

# 结构体描述解析
struct_parser_registry = {
    SpreadSheetParser.name(): SpreadSheetParser(),
}

# 源代码生成
code_generator_registry = {
    CppStructGenerator.name(): CppStructGenerator(),
    # CSharpStructGenerator.name(): CSharpStructGenerator(),
    GoStructGenerator.name(): GoStructGenerator(),
    # JavaStructGenerator.name(): JavaStructGenerator(),
}

# 数据文件写入
data_writer_registry = {
    CsvDataWriter.name(): CsvDataWriter(),
    JsonDataWriter.name(): JsonDataWriter(),
}


# 数据结构解析
def get_struct_parser(name: str):
    return struct_parser_registry.get(name, None)


# 代码生成
def get_code_generator(name: str):
    return code_generator_registry.get(name, None)


# 数据转换
def get_data_writer(name: str):
    return data_writer_registry.get(name, None)
