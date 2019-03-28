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

# data importers
importer_registry = {
    ExcelImporter.name(): ExcelImporter(),
    MySQLImporter.name(): MySQLImporter(),
}

# source generators
generator_registry = {
    CppV1Generator.name(): CppV1Generator(),
    CSV1Generator.name(): CSV1Generator(),
    GoV1Generator.name(): GoV1Generator(),
    GoV2Generator.name(): GoV2Generator(),
    JavaV1Generator.name(): JavaV1Generator(),
}


def get_importer(name):
    return importer_registry.get(name, None)


def get_generator(name):
    return generator_registry.get(name, None)
