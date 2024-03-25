"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import csv
import os
import codecs
import xlrd
import openpyxl
import tabugen.predef as predef


def is_ignored_filename(filename: str) -> bool:
    for text in ['~$', '-TNP-', ' - 副本']:
        if filename.find(text) >= 0:
            return True
    return False


# 从路径种搜索所有excel文件
def enum_spreadsheet_files(rootdir: str):
    files = []
    for dirpath, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            if filename.endswith(".xlsx") or filename.endswith(".xls") or filename.endswith(".csv"):
                files.append(dirpath + os.sep + filename)
    filenames = []
    for filename in files:
        if not is_ignored_filename(filename):
            filename = os.path.abspath(filename)
            filenames.append(filename)
    return filenames


# 读取第一个sheet为数据和meta sheet
def read_workbook_table(filename: str):
    print('load workbook', filename)
    if filename.endswith('.xlsx'):
        return __xlsx_read_workbook(filename)
    elif filename.endswith('.xls'):
        return __xlsx_read_workbook(filename)
    elif filename.endswith('.csv'):
        return __read_csv_to_table(filename)
    else:
        return [], {}


def parse_meta_table(table):
    meta = {}
    for row in table:
        if len(row) >= 2:
            key = row[0].strip()
            value = row[1].strip()
            if len(key) > 0 and len(value) > 0:
                meta[key] = value
    return meta


def __read_csv_to_table(filename: str):
    table = []
    meta = {}
    with codecs.open(filename, 'r', 'utf-8') as csvf:
        reader = csv.reader(csvf, skipinitialspace=True)
        for row in reader:
            is_empty_row = True  # 是否一行全部是空字符串
            for text in row:
                if len(text) > 0:
                    is_empty_row = False
                    break
            if not is_empty_row:
                table.append(row)

    name = os.path.splitext(os.path.basename(filename))
    meta[predef.PredefClassName] = name
    return table, meta


def __xlsx_read_sheet_to_table(sheet):
    table = []
    for i, sheet_row in enumerate(sheet.rows):
        row = []
        is_empty_row = True  # 是否一行全部是空字符串
        for j, cell in enumerate(sheet_row):
            text = ''
            if cell.value is not None:
                text = str(cell.value).strip()
            if len(text) > 0:
                is_empty_row = False
            row.append(text.strip())
        if not is_empty_row:
            table.append(row)
    return table


# 使用openpyxl读取excel文件（.xlsx后缀格式）
def __xlsx_read_workbook(filename: str):
    workbook = openpyxl.load_workbook(filename, data_only=True, read_only=True)
    sheet_names = workbook.sheetnames
    if len(sheet_names) == 0:
        workbook.close()
        return [], {}
    if sheet_names[0] == predef.PredefMetaSheet:
        workbook.close()
        return [], {}

    first_sheet = workbook[sheet_names[0]]
    data = __xlsx_read_sheet_to_table(first_sheet)
    meta = {}
    if predef.PredefMetaSheet in sheet_names:
        meta_sheet = workbook[predef.PredefMetaSheet]
        meta = parse_meta_table(__xlsx_read_sheet_to_table(meta_sheet))

    if predef.PredefClassName not in meta:
        meta[predef.PredefClassName] = sheet_names[0]

    workbook.close()
    return data, meta


def __xls_read_sheet_to_table(sheet):
    table = []
    for rx in range(sheet.nrows):
        cell_row = sheet.row(rx)
        row = []
        is_empty_row = True  # 是否一行全部是空字符串
        for cell in cell_row:
            text = str(cell.value).strip()
            if len(text) > 0:
                is_empty_row = False
            row.append(text)
        if not is_empty_row:
            table.append(row)
    return table


# 使用xlrd读取excel文件(.xls后缀格式）
def __xls_read_workbook(filename: str):
    workbook = xlrd.open_workbook(filename, on_demand=True)
    sheet_names = workbook.sheet_names()
    if len(sheet_names) == 0:
        return [], {}
    if sheet_names[0] == predef.PredefMetaSheet:
        return [], {}

    first_sheet = workbook.sheet_by_name(sheet_names[0])
    data = __xls_read_sheet_to_table(first_sheet)
    meta = {}
    if predef.PredefMetaSheet in sheet_names:
        meta_sheet = workbook[predef.PredefMetaSheet]
        meta = parse_meta_table(__xls_read_sheet_to_table(meta_sheet))

    if predef.PredefClassName not in meta:
        meta[predef.PredefClassName] = sheet_names[0]

    return data, meta
