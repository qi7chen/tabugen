# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

from taksi.parser.excel import ExcelStructParser
from taksi.parser.mysql import MySQLStructParser

from taksi.generator.cpp.gen_csv_load import CppCsvLoadGenerator
from taksi.generator.csharp.gen_csv_load import CSharpCsvLoadGenerator
from taksi.generator.csharp.gen_json_load import CSharpJsonLoadGenerator
from taksi.generator.java.gen_csv_load import JavaCsvLoadGenerator
from taksi.generator.java.gen_json_load import JavaJsonLoadGenerator
from taksi.generator.go.gen_csv_load import GoCsvLoadGenerator
from taksi.generator.go.gen_json_load import GoJsonLoadGenerator
from taksi.generator.go.gen_sql_orm import GoSqlOrmGenerator


# struct parser
struct_parser_registry = {
    ExcelStructParser.name(): ExcelStructParser(),
    MySQLStructParser.name(): MySQLStructParser(),
}

# code generators
code_generator_registry = {
    CppCsvLoadGenerator.name(): CppCsvLoadGenerator(),
    CSharpCsvLoadGenerator.name(): CSharpCsvLoadGenerator(),
    CSharpJsonLoadGenerator.name(): CSharpJsonLoadGenerator(),
    JavaCsvLoadGenerator.name(): JavaCsvLoadGenerator(),
    JavaJsonLoadGenerator.name(): JavaJsonLoadGenerator(),
    GoCsvLoadGenerator.name(): GoCsvLoadGenerator(),
    GoJsonLoadGenerator.name(): GoJsonLoadGenerator(),
    GoSqlOrmGenerator.name(): GoSqlOrmGenerator(),
}

# data format transform
data_transformer_registry = {

}


# get data generator by name
def get_struct_parser(name):
    return struct_parser_registry.get(name, None)


# get code generator by name
def get_code_generator(name):
    return code_generator_registry.get(name, None)


def get_data_transformer(name):
    return data_transformer_registry.get(name, None)
