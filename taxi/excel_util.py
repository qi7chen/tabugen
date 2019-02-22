# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import openpyxl
import descriptor

# read to workbook and its sheet names
def read_workbook_and_sheet_names(filename):
    wb = openpyxl.load_workbook(filename, data_only=True)
    return wb, wb.sheetnames

# read sheet data to csv rows
def read_workbook_sheet_to_csv(workbook, sheet_name):
    rows = []
    sheet = workbook[sheet_name]
    assert sheet is not None, sheet_name
    for i, sheet_row in enumerate(sheet.rows):
        row = []
        for j, cell in enumerate(sheet_row):
            text = ''
            if cell.value is not None:
                text = str(cell.value)
            row.append(text.strip())
        rows.append(row)
    return rows


# 有些数据在excel里输入为整数，但存储形式为浮点数
def validate_data_rows(rows, struct):
    new_rows = []
    fields = struct['fields']
    for row in rows:
        assert len(row) >= len(fields), (len(fields), len(row), row)
        for j in range(len(row)):
            if j >= len(fields):
                continue
            typename = fields[j]['type_name']
            if descriptor.is_integer_type(typename) and len(row[j]) > 0:
                f = float(row[j])  # test if ok
                if row[j].find('.') >= 0:
                    print('round interger', row[j], '-->', round(f))
                    row[j] = str(round(float(row[j])))
            else:
                if descriptor.is_floating_type(typename) and len(row[j]) > 0:
                    f = float(row[j])  # test if ok

        # skip all empty row
        is_all_empty = True
        for text in row:
            if len(text.strip()) > 0:
                is_all_empty = False
                break
        if not is_all_empty:
            new_rows.append(row)
    return new_rows