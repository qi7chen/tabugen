# Copyright (C) 2018-present ki7chen@github. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import csv
import os
import codecs
import xlrd
import openpyxl
from xlrd.sheet import Sheet
from openpyxl.worksheet.worksheet import Worksheet
import tabugen.predef as predef
import tabugen.util.tableutil as tableutil


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
def read_workbook_table(filename: str, meta: dict) -> list[list[str]]:
    print('start load workbook', filename)
    if filename.endswith('.xlsx'):
        workbook = openpyxl.load_workbook(filename, data_only=True, read_only=True)
        sheet_names = workbook.sheetnames
        if len(sheet_names) == 0:
            workbook.close()
            return []
        first_sheet = workbook[sheet_names[0]]
        table = __xlsx_read_sheet_to_table(first_sheet)
        parse_sheet_table(filename, sheet_names[0], table, meta)
        return table
    elif filename.endswith('.xls'):
        workbook = xlrd.open_workbook(filename)
        sheet_names = workbook.sheet_names()
        if len(sheet_names) == 0:
            return []
        first_sheet = workbook.sheet_by_name(sheet_names[0])
        table = __xls_read_sheet_to_table(first_sheet)
        parse_sheet_table(filename, sheet_names[0], table, meta)
        return table
    elif filename.endswith('.csv'):
        meta[predef.PredefClassName] = os.path.splitext(os.path.basename(filename))
        return __read_csv_to_table(filename)
    else:
        return []


def parse_sheet_table(filename: str, sheet_name: str, table: list[list[str]], meta: dict):
    meta[predef.PredefParseKVMode] = False
    if sheet_name.startswith('@'):
        meta[predef.PredefParseKVMode] = True
        sheet_name = sheet_name[1:]
    else:
        meta[predef.PredefParseKVMode] = tableutil.is_kv_table(table)

    # 如果没有指定类名，使用文件名
    if predef.PredefClassName not in meta:
        if not is_default_sheet_name(sheet_name) and sheet_name.isalpha():
            meta[predef.PredefClassName] = sheet_name
        else:
            name = os.path.splitext(os.path.basename(filename))[0]
            meta[predef.PredefClassName] = name


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


def __read_csv_to_table(filename: str) -> list[list[str]]:
    table = []
    with codecs.open(filename, 'r', 'utf-8') as f:
        for csv_row in csv.reader(f, skipinitialspace=True):
            row = [try_conv_float_int(text) for text in csv_row]
            row_len = sum(len(s) for s in row)
            if row_len > 0:
                table.append(row)
    return table


# 使用openpyxl读取excel文件（.xlsx格式）
def __xlsx_read_sheet_to_table(sheet: Worksheet) -> list[list[str]]:
    table = []
    for i, sheet_row in enumerate(sheet.rows):
        row = []
        row_len = 0
        for j, cell in enumerate(sheet_row):
            text = ''
            if cell.value:
                text = str(cell.value).strip()
                if len(text) > 0:
                    row_len += len(text)
                    text = try_conv_float_int(text)
            row.append(text)
        if row_len > 0:
            table.append(row)  # 剔除全空白行
    return table


# 使用xlrd读取excel文件(.xls后缀格式）
def __xls_read_sheet_to_table(sheet: Sheet) -> list[list[str]]:
    table = []
    for i in range(sheet.nrows):
        cell_row = sheet.row(i)
        row = []
        row_len = 0
        for cell in cell_row:
            text = str(cell.value).strip()
            if len(text) > 0:
                row_len += len(text)
                text = try_conv_float_int(text)
            row.append(text)
        if row_len > 0:
            table.append(row)
    return table
