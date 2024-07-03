# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import csv
import codecs
import tempfile
import filecmp
import shutil
from argparse import Namespace
import tabugen.util.helper as helper
import tabugen.util.tableutil as tableutil
from tabugen.structs import Struct


# 写入csv文件
class CsvDataWriter:
    def __init__(self):
        pass

    @staticmethod
    def name() -> str:
        return "csv"

    # 将数据写入csv文件
    @staticmethod
    def write_file(name: str, table: list[list[str]], filepath: str, encoding: str):
        tmp_filename = '%s/tabular_%s' % (tempfile.gettempdir(), helper.random_word(8))
        os.path.join(tempfile.gettempdir())
        filename = os.path.abspath(tmp_filename)
        f = codecs.open(filename, "w", encoding)
        w = csv.writer(f, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        w.writerows(table)
        f.close()

        target_filename = os.path.join(filepath, name + ".csv")

        # move to destination path if content not equal
        if os.path.isfile(target_filename) and filecmp.cmp(tmp_filename, target_filename):
            os.remove(tmp_filename)
        else:
            shutil.move(tmp_filename, target_filename)
            print("wrote csv file to", target_filename)

    #
    def parse_table(self, struct: Struct):
        data = struct.data_rows
        data = tableutil.validate_unique_column(struct, data)
        data = tableutil.convert_table_data(struct, data)
        data = tableutil.table_remove_comment_columns(struct.field_columns, data)
        return [struct.field_names] + data

    def process(self, descriptors: list[Struct], args: Namespace):
        filepath = args.out_data_path
        encoding = args.data_file_encoding
        if filepath != '.':
            try:
                print('make dir', filepath)
                os.makedirs(filepath)
            except OSError as e:
                pass

        print('csv output path is', filepath)
        for struct in descriptors:
            table = self.parse_table(struct)
            name = helper.camel_to_snake(struct.camel_case_name)
            self.write_file(name, table, filepath, encoding)
