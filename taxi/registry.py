# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

from taxi.importer.excel import ExcelImporter
from taxi.importer.mysql import MySQLImporter
from taxi.generator.cppv1 import CppV1Generator
from taxi.generator.csv1 import CSV1Generator
from taxi.generator.javav1 import JavaV1Generator
from taxi.generator.gov1 import GoV1Generator
from taxi.generator.gov2 import GoV2Generator

from taxi.datagen.csv import CsvDataGen
from taxi.datagen.json import JsonDataGen

# data importers
importer_registry = {
    ExcelImporter.name(): ExcelImporter(),
    MySQLImporter.name(): MySQLImporter(),
}

# code generators
code_generator_registry = {
    CppV1Generator.name(): CppV1Generator(),
    CSV1Generator.name(): CSV1Generator(),
    GoV1Generator.name(): GoV1Generator(),
    GoV2Generator.name(): GoV2Generator(),
    JavaV1Generator.name(): JavaV1Generator(),
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
