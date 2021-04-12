# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import csv
import codecs
import tempfile
import filecmp
import shutil
import tabugen.util.strutil as strutil
import tabugen.util.rowutil as rowutil


# 写入csv文件
class CsvDataWriter:
    def __init__(self):
        pass

    @staticmethod
    def name():
        return "csv"

    # 将数据写入csv文件
    def write_file(self, name, rows, delim, filepath, encoding):
        tmp_filename = '%s/tabular_%s' % (tempfile.gettempdir(), strutil.random_word(10))
        filename = os.path.abspath(tmp_filename)
        f = codecs.open(filename, "w", encoding)
        w = csv.writer(f, delimiter=delim, lineterminator='\n', quotechar='"', quoting=csv.QUOTE_ALL)
        w.writerows(rows)
        f.close()

        target_filename = "%s/%s.csv" % (filepath, name)

        # move to destination path if content not equal
        if os.path.isfile(target_filename) and filecmp.cmp(tmp_filename, target_filename):
            os.remove(tmp_filename)
        else:
            shutil.move(tmp_filename, target_filename)
            print("wrote csv rows to", target_filename)

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
            rows = struct["data_rows"]
            rows = rowutil.validate_unique_column(struct, rows)
            rows = rowutil.hide_skipped_row_fields(args.enable_column_skip, struct, rows)
            name = strutil.camel_to_snake(struct['camel_case_name'])
            self.write_file(name, rows, args.out_csv_delim, filepath, encoding)
