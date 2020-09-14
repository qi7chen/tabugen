# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import taksi.predef as predef
import taksi.xlsxhelp as xlsxhelp

class ExcelDataTransform:

    def __init__(self):
        pass

    @staticmethod
    def name():
        return "excel"

    # load data from file
    def load(self, struct, filename):
        assert os.path.isfile(filename)
        meta = struct["options"]
        wb, sheet_names = xlsxhelp.read_workbook_and_sheet_names(filename)
        assert len(sheet_names) > 0
        sheet_name = meta.get(predef.PredefTargetFileSheet, sheet_names[0])
        sheet_rows = xlsxhelp.read_workbook_sheet_to_rows(wb, sheet_name)

        data_start_index = int(meta[predef.PredefDataStartRow])
        data_end_index = len(sheet_rows)
        if predef.PredefDataEndRow in meta:
            data_end_index = int(meta[predef.PredefDataEndRow])

        data_rows = sheet_rows[data_start_index - 1: data_end_index]
        data_rows = self.pad_data_rows(data_rows, struct)
        data_rows = xlsxhelp.validate_data_rows(data_rows, struct)
        return data_rows

    # 对齐数据行
    def pad_data_rows(self, rows, struct):
        # pad empty row
        max_row_len = len(struct['fields'])
        for row in rows:
            if len(row) > max_row_len:
                max_row_len = len(row)

            for i in range(len(row)):
                for j in range(len(row), max_row_len):
                    rows[i].append("")

        # 删除未导出的列
        new_rows = []
        fields = sorted(struct['fields'], key=lambda fld: fld['column_index'])
        for row in rows:
            new_row = []
            for field in fields:
                new_row.append(row[field['column_index'] - 1])
            new_rows.append(new_row)
        return new_rows

    # store data rows into xlsx
    def store(self, data_rows, struct, filename):
        raise RuntimeError("we cannot store data rows into xlsx right now")
