# Copyright (C) 2019-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import csv
import codecs
import taxi.descriptor.predef as predef
import taxi.descriptor.strutil as strutil

class CsvDataGen:
    def __init__(self):
        pass

    @staticmethod
    def name():
        return "csv"

    def run(self, descriptors, args):
        datadir = args.get(predef.OptionOutDataDir, '.')
        if datadir != '.':
            try:
                print('make dir', datadir)
                os.makedirs(datadir)
            except Exception as e:
                pass

        for struct in descriptors:
            rows = struct["data_rows"]
            rows = self.validate_unique_column(struct, rows, args)
            rows = self.hide_unused_rows(struct, rows, args)
            self.write_file(struct, datadir, rows, args)

    # 检查唯一主键
    def validate_unique_column(self, struct, rows, params):
        if struct['options'][predef.PredefParseKVMode]:
            return rows

        # TO-DO
        return rows

    # 置空不必要显示的内容
    def hide_unused_rows(self, struct, rows, params):
        if struct['options'][predef.PredefParseKVMode]:
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
    def write_file(self, struct, datadir, rows, params):
        encoding = params.get(predef.OptionDataEncoding, 'utf-8')
        filename = "%s/%s.csv" % (datadir, strutil.camel_to_snake(struct['camel_case_name']))
        filename = os.path.abspath(filename)
        f = codecs.open(filename, "w", encoding)
        w = csv.writer(f)
        w.writerows(rows)
        f.close()
        print("wrote csv data to", filename)
