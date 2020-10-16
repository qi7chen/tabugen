# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import csv
import codecs
import taksi.predef as predef
import taksi.strutil as strutil


class CsvDataWriter:
    def __init__(self):
        pass

    @staticmethod
    def name():
        return "csv"

    # 检查唯一主键
    def validate_unique_column(self, struct, rows):
        if struct['options'][predef.PredefParseKVMode]:
            return rows

        # TO-DO
        return rows

    # 置空不必要显示的内容
    def hide_unused_rows(self, struct, rows, params):
        if predef.PredefValueTypeColumn in struct['options']:
            typecol = int(struct['options'][predef.PredefValueTypeColumn])
            commentcol = int(struct['options'][predef.PredefCommentColumn])
            for row in rows:
                row[typecol - 1] = ''
                row[commentcol - 1] = ''
        else:
            if predef.OptionHideColumns in params:
                text = struct["options"].get(predef.PredefHideColumns, "")
                text = text.strip()
                if len(text) > 0:
                    columns = [int(x.strip()) for x in text.split(',')]
                    for row in rows:
                        for idx in columns:
                            row[idx - 1] = ''
        return rows

    # 将数据写入csv文件
    def write_file(self, name, rows, delim, filepath, encoding):
        filename = "%s/%s.csv" % (filepath, name)
        filename = os.path.abspath(filename)
        f = codecs.open(filename, "w", encoding)
        w = csv.writer(f, delimiter=delim, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        for row in rows:
            w.writerow(row)
        f.close()
        print("wrote csv rows to", filename)

    def process(self, descriptors, args):
        filepath = args.out_data_path
        encoding = args.data_file_encoding
        if filepath != '.':
            try:
                print('make dir', filepath)
                os.makedirs(filepath)
            except Exception as e:
                pass

        for struct in descriptors:
            rows = struct["data_rows"]
            rows = self.validate_unique_column(struct, rows)
            # rows = self.hide_unused_rows(struct, rows)
            name = strutil.camel_to_snake(struct['camel_case_name'])
            self.write_file(name, rows, args.out_csv_delim, filepath, encoding)
