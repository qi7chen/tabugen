# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import csv
import codecs
import tempfile
import filecmp
import shutil
import tabugen.predef as predef
import tabugen.util.strutil as strutil
import tabugen.util.tableutil as rowutil


# 写入csv文件
class CsvDataWriter:
    def __init__(self):
        pass

    @staticmethod
    def name() -> str:
        return "csv"

    # 将数据写入csv文件
    @staticmethod
    def write_file(name, table, filepath, encoding):
        tmp_filename = '%s/tabular_%s' % (tempfile.gettempdir(), strutil.random_word(10))
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
            print("wrote csv rows to", target_filename)

    @staticmethod
    def header_row(struct):
        row = []
        for field in struct['fields']:
            row.append(field['name'])
        return row

    # 只保留key-value
    def parse_kv_table(self, struct):
        table = []
        data_rows = struct['data_rows']
        for row in data_rows:
            name = row[predef.PredefKeyColumn]
            value = row[predef.PredefValueColumn]
            table.append([name, value])
        return table

    #
    def parse_table(self, struct):
        data = struct["data_rows"]
        data = rowutil.validate_unique_column(struct, data)
        return data

    def process(self, descriptors, args):
        filepath = args.out_data_path
        encoding = args.data_file_encoding
        if filepath != '.':
            try:
                print('make dir', filepath)
                os.makedirs(filepath)
            except OSError as e:
                pass

        for struct in descriptors:
            if predef.PredefParseKVMode in struct['options']:
                table = self.parse_kv_table(struct)
            else:
                table = self.parse_table(struct)
            name = strutil.camel_to_snake(struct['camel_case_name'])
            self.write_file(name, table, filepath, encoding)
