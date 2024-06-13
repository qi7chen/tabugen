# Copyright (C) 2018-present ki7chen@github. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import csv
import os
import codecs
import xlrd
import openpyxl
import tabugen.predef as predef
from xlrd.sheet import Sheet
from openpyxl.worksheet.worksheet import Worksheet


def is_ignored_filename(filename: str) -> bool:
    return any(text in filename for text in ['~$', '-TNP-', ' - 副本'])


def is_default_sheet_name(name: str) -> bool:
    try:
        int(name[name.find('Sheet') + 1:])
        return True
    except ValueError:
        return False


# 从路径种搜索所有excel文件
def enum_spreadsheet_files(rootdir: str) -> list[str]:
    files = []
    for dirpath, _, filenames in os.walk(rootdir):
        for filename in filenames:
            if filename.endswith(('.xlsx', 'xls', '.csv')):
                files.append(dirpath + os.sep + filename)
    filenames = []
    for filename in files:
        if not is_ignored_filename(filename):
            filename = os.path.abspath(filename)
            filenames.append(filename)
    return filenames


# 读取第一个sheet为数据和meta sheet
def read_workbook_table(filename: str) -> (list[list[str]], object):
    print('start load workbook', filename)
    if filename.endswith('.xlsx'):
        return __xlsx_read_workbook(filename)
    elif filename.endswith('.xls'):
        return __xls_read_workbook(filename)
    elif filename.endswith('.csv'):
        return __read_csv_to_table(filename)
    else:
        return [], {}


def parse_meta_table(table: list[list[str]]) -> dict[str, str]:
    return {row[0].strip(): row[1].strip() for row in
            table if len(row) >= 2 and row[0].strip() and row[1].strip()}


def try_conv_float_int(text: str) -> str:
    if text.find('.') <= 0:
        return text
    try:
        f = float(text)
        if f.is_integer():
            return str(int(f))
    except ValueError:
        pass
    return text


def __read_csv_to_table(filename: str) -> (list[str], dict[str, str]):
    meta = {}
    with codecs.open(filename, 'r', 'utf-8') as f:
        table = [row for row in csv.reader(f, skipinitialspace=True) if any(text for text in row)]  # 剔除全空白行
    meta[predef.PredefClassName] = os.path.splitext(os.path.basename(filename))
    return table, meta


def __xlsx_read_sheet_to_table(sheet: Worksheet) -> list[list[str]]:
    table = []
    for i, sheet_row in enumerate(sheet.rows):
        row = []
        is_empty_row = True  # 是否一行全部是空字符串
        for j, cell in enumerate(sheet_row):
            text = ''
            if cell.value:
                text = str(cell.value).strip()
            if len(text) > 0:
                is_empty_row = False
            text = try_conv_float_int(text)
            row.append(text)
        if not is_empty_row:
            table.append(row)
    return table


# 使用openpyxl读取excel文件（.xlsx格式）
def __xlsx_read_workbook(filename: str) -> (list[str], dict[str, str]):
    workbook = openpyxl.load_workbook(filename, data_only=True, read_only=True)
    sheet_names = workbook.sheetnames
    if len(sheet_names) == 0:
        workbook.close()
        return [], {}
    if sheet_names[0] == predef.PredefMetaSheet:
        workbook.close()
        return [], {}

    meta = {}
    meta[predef.PredefParseKVMode] = sheet_names[0].startswith('@')
    first_sheet = workbook[sheet_names[0]]
    data = __xlsx_read_sheet_to_table(first_sheet)
    if predef.PredefMetaSheet in sheet_names:
        meta_sheet = workbook[predef.PredefMetaSheet]
        meta = parse_meta_table(__xlsx_read_sheet_to_table(meta_sheet))

    # 如果没有指定类名，使用文件名
    if predef.PredefClassName not in meta:
        if not is_default_sheet_name(sheet_names[0]) and sheet_names[0].isalpha():
            meta[predef.PredefClassName] = sheet_names[0]
        else:
            name = os.path.splitext(os.path.basename(filename))[0]
            meta[predef.PredefClassName] = name

    workbook.close()
    return data, meta



def __xls_read_sheet_to_table(sheet: Sheet) -> list[list[str]]:
    table = []
    for i in range(sheet.nrows):
        comments = {}
        cell_row = sheet.row(i)
        row = []
        is_empty_row = True  # 是否一行全部是空字符串
        for cell in cell_row:
            text = str(cell.value).strip()
            if len(text) > 0:
                is_empty_row = False
            text = try_conv_float_int(text)
            row.append(text)
        if not is_empty_row:
            table.append(row)
    return table


# 使用xlrd读取excel文件(.xls后缀格式）
def __xls_read_workbook(filename: str) -> (list[list[str]], object):
    workbook = xlrd.open_workbook(filename, on_demand=True)
    sheet_names = workbook.sheet_names()
    if len(sheet_names) == 0 or sheet_names[0] == predef.PredefMetaSheet:
        return [], {}

    meta = {}
    meta[predef.PredefParseKVMode] = sheet_names[0].startswith('@')
    first_sheet = workbook.sheet_by_name(sheet_names[0])
    data = __xls_read_sheet_to_table(first_sheet)
    if predef.PredefMetaSheet in sheet_names:
        meta_sheet = workbook[predef.PredefMetaSheet]
        meta = parse_meta_table(__xls_read_sheet_to_table(meta_sheet))

    # 如果没有指定类名，使用文件名
    if predef.PredefClassName not in meta:
        if not is_default_sheet_name(sheet_names[0]) and sheet_names[0].isalpha():
            meta[predef.PredefClassName] = sheet_names[0]
        else:
            name = os.path.splitext(os.path.basename(filename))[0]
            meta[predef.PredefClassName] = name

    return data, meta
