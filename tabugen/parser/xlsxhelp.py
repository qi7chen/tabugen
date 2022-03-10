# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.
import typing

import openpyxl
import xlrd

import tabugen.typedef as types

ignored_extension = [
    '~$',
    '-TNP-',
    ' - 副本',
]


def is_ignored_filename(filename: str) -> bool:
    for text in ignored_extension:
        if filename.find(text) >= 0:
            return True
    return False


# read to workbook and its sheet names
def read_workbook_sheet_names(filename: str):
    if filename.endswith('.xls'):
        return __xlrd_read_workbook_sheet_names(filename)
    elif filename.endswith('.xlsx'):
        return __openpyxl_read_workbook_sheet_names(filename)
    else:
        raise RuntimeError('file %s extension not recognized' % filename)


def __xlrd_read_workbook_sheet_names(filename: str):
    book = xlrd.open_workbook(filename, on_demand=True)
    return book.sheet_names()


def __openpyxl_read_workbook_sheet_names(filename: str):
    wb = openpyxl.load_workbook(filename, data_only=True, read_only=True)
    wb.close()
    return wb.sheetnames


def read_workbook_sheet_to_rows(filename: str, sheet_name: str):
    print('load workbook', filename)
    if filename.endswith('.xls'):
        return __xlrd_read_workbook_sheet_to_rows(filename, sheet_name)
    elif filename.endswith('.xlsx'):
        return __openpyxl_read_workbook_sheet_to_rows(filename, sheet_name)
    else:
        raise RuntimeError('file %s extension not recognized' % filename)


def __xlrd_read_workbook_sheet_to_rows(filename: str, sheet_name: str):
    book = xlrd.open_workbook(filename, on_demand=True)
    sheet = book.sheet_by_name(sheet_name)
    rows = []
    for rx in range(sheet.nrows):
        row = sheet.row(rx)
        new_row = []
        for cell in row:
            new_row.append(str(cell.value))
        rows.append(new_row)
    return rows


#
def __openpyxl_read_workbook_sheet_to_rows(filename: str, sheet_name: str):
    print('load workbook', filename)
    wb = openpyxl.load_workbook(filename, data_only=True, read_only=True)
    sheet = wb.get_sheet_by_name(sheet_name)
    rows = []
    assert sheet is not None, sheet_name
    for i, sheet_row in enumerate(sheet.rows):
        row = []
        for j, cell in enumerate(sheet_row):
            text = ''
            if cell.value is not None:
                text = str(cell.value)
            row.append(text.strip())
        rows.append(row)
    wb.close()
    return rows


# TODO:
def close_workbook(wb):
    wb.close()


# 有些数据在excel里输入为整数，但存储形式为浮点数
def validate_data_rows(rows: typing.Sequence, struct: typing.Mapping):
    new_rows = []
    fields = struct['fields']
    for row in rows:
        assert len(row) >= len(fields), (len(fields), len(row), row)
        for j in range(len(row)):
            if j >= len(fields):
                continue
            typename = fields[j]['type_name']
            if types.is_integer_type(typename) and len(row[j]) > 0:
                f = float(row[j])  # test if ok
                if row[j].find('.') >= 0:
                    print('round integer', row[j], '-->', round(f))
                    row[j] = str(round(float(row[j])))
            else:
                if types.is_floating_type(typename) and len(row[j]) > 0:
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
