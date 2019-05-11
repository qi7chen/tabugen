# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

from taxi.importer.excel import ExcelImporter
from taxi.importer.mysql import MySQLImporter

from taxi.generator.cpp.gen_csv_load import CppCsvLoadGenerator
from taxi.generator.csharp.gen_csv_load import CSharpCsvLoadGenerator
from taxi.generator.java.gen_csv_load import JavaCsvLoadGenerator
from taxi.generator.go.gen_csv_load import GoCsvLoadGenerator
from taxi.generator.go.gen_sql_orm import GoSqlOrmGenerator

from taxi.datagen.csv import CsvDataGen
from taxi.datagen.json import JsonDataGen

# data importers
importer_registry = {
    ExcelImporter.name(): ExcelImporter(),
    MySQLImporter.name(): MySQLImporter(),
}

# code generators
code_generator_registry = {
    CppCsvLoadGenerator.name(): CppCsvLoadGenerator(),
    CSharpCsvLoadGenerator.name(): CSharpCsvLoadGenerator(),
    JavaCsvLoadGenerator.name(): JavaCsvLoadGenerator(),
    GoCsvLoadGenerator.name(): GoCsvLoadGenerator(),
    GoSqlOrmGenerator.name(): GoSqlOrmGenerator(),
}

# data generators
data_generator_registry = {
    CsvDataGen.name(): CsvDataGen(),
    JsonDataGen.name(): JsonDataGen(),
}


def get_importer(name):
    return importer_registry.get(name, None)


# get code generator by name
def get_code_generator(name):
    return code_generator_registry.get(name, None)


# get data generator by name
def get_data_generator(name):
    return data_generator_registry.get(name, None)
