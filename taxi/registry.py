# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

from importer_excel import ExcelImporter
from importer_mysql import MySQLImporter
from gen_cpp_v1 import CppV1Generator
from gen_cs_v1 import CSV1Generator
from gen_go_v1 import GoV1Generator
from gen_go_v2 import GoV2Generator

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
}




def get_importer(name):
    return importer_registry[name]





def get_generator(name):
    return generator_registry[name]
