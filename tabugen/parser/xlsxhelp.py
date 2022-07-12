"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import os
import openpyxl
import xlrd
import tabugen.util.tableutil as tableutil
import tabugen.predef as predef

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


# 从路径种搜索所有excel文件
def enum_excel_files(rootdir: str):
    files = []
    for dirpath, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            if filename.endswith(".xlsx") or filename.endswith(".xls"):
                files.append(dirpath + os.sep + filename)
    filenames = []
    for filename in files:
        if not is_ignored_filename(filename):
            filename = os.path.abspath(filename)
            filenames.append(filename)
    return filenames


# 读取第一个sheet为数据和meta sheet
def read_workbook_data(filename: str):
    print('load workbook', filename)
    if filename.endswith('.xls'):
        workbook = xlrd.open_workbook(filename, on_demand=True)
        sheet_names = workbook.sheet_names()
        read_sheet = __xlrd_read_workbook_sheet
    elif filename.endswith('.xlsx'):
        workbook = openpyxl.load_workbook(filename, data_only=True, read_only=True)
        sheet_names = workbook.sheetnames
        read_sheet = __openpyxl_read_workbook_sheet
    else:
        raise RuntimeError('file %s extension not recognized' % filename)

    if len(sheet_names) == 0:
        return {}, {}
    if len(sheet_names) == 1 and sheet_names[0] == predef.PredefMetaSheet:
        meta = read_sheet(workbook, predef.PredefMetaSheet)
        return {}, meta

    table = read_sheet(workbook, sheet_names[0])   # first sheet
    meta = {}
    if predef.PredefMetaSheet in sheet_names:
        meta_table = read_sheet(workbook, predef.PredefMetaSheet)
        meta = tableutil.parse_meta(meta_table)

    if predef.PredefClassName not in meta:
        meta[predef.PredefClassName] = sheet_names[0]

    if filename.endswith('.xlsx'):
        workbook.close()

    return table, meta


# 使用xlrd读取excel文件(.xls后缀格式）
def __xlrd_read_workbook_sheet(workbook, sheet_name: str):
    sheet = workbook.sheet_by_name(sheet_name)
    table = []
    for rx in range(sheet.nrows):
        cell_row = sheet.row(rx)
        row = []
        empty_row = True
        for cell in cell_row:
            text = str(cell.value).strip()
            if len(text) > 0:
                empty_row = False
            row.append(text)
        if not empty_row:
            table.append(row)
    table = tableutil.trim_empty_columns(table)
    return table


# 使用openpyxl读取excel文件（.xlsx后缀格式）
def __openpyxl_read_workbook_sheet(workbook, sheet_name: str):
    sheet = workbook[sheet_name]
    table = []
    assert sheet is not None, sheet_name
    for i, sheet_row in enumerate(sheet.rows):
        row = []
        row_empty = True
        for j, cell in enumerate(sheet_row):
            text = ''
            if cell.value is not None:
                text = str(cell.value).strip()
            if len(text) > 0:
                row_empty = False
            row.append(text.strip())
        if not row_empty:
            table.append(row)
    table = tableutil.trim_empty_columns(table)
    return table
