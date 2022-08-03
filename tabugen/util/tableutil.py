"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import sys

import tabugen.predef as predef
import tabugen.typedef as types
import tabugen.util.strutil as strutil


# 删除首部和尾部连续的空列
def trim_empty_columns(table):
    header = table[0]   # 第一行为头部
    end = len(header)
    start = 0
    while start < end:
        stop = True
        if len(header[end - 1]) == 0:
            end -= 1
            stop = False
        if len(header[start]) == 0:
            start += 1
            stop = False
        if stop:
            break

    if start > 0 or end < len(header):
        for i in range(len(table)):
            table[i] = table[i][start:end]
    return table


# 删除table的某一列
def remove_one_column(table, column: int):
    for col in range(len(table)):
        row = table[col]
        if column < len(row):
            row = row[:column] + row[column + 1:]
            table[col] = row
    return table


# 删除空白列(在中间的列）
def remove_empty_columns(table):
    header = table[0]
    col = len(header)
    while col > 0:
        col -= 1
        field = header[col]
        # 名字为空白的列、以#或者//开头的列需要删除
        if len(field) == 0 or field.startswith('#') or field.startswith('//'):
            table = remove_one_column(table, col)
    return table


# 是否字段内容唯一
def is_all_row_field_value_unique(rows, col: int):
    all_set = {}
    for i, row in enumerate(rows):
        if len(row[col]) > 0:
            value = row[col]
            if value in all_set:
                return False, i, all_set[value]
            else:
                all_set[value] = i
    return True, 0, 0


# 检查唯一主键
def validate_unique_column(struct, rows):
    if struct['options'][predef.PredefParseKVMode]:
        return rows

    if predef.OptionUniqueColumns not in struct['options']:
        return rows
    names = struct['options'][predef.OptionUniqueColumns]
    if len(names) == 0:
        return rows
    for field in struct['fields']:
        if field['name'] in names:
            col = field['column_index']
            (is_unique, row_line, exist_line) = is_all_row_field_value_unique(rows, col)
            if not is_unique:
                print('duplicate field %s value found, row %d and row %d' % (field['name'], exist_line, row_line))
                sys.exit(1)
    return rows


# 处理一下数据
# 1，配置的数值类型如果为空，默认填充0
# 2，如果配置的类型是整数，但实际有浮点，需要转换成整数
def convert_table_data(struct, data):
    fields = struct['fields']
    for col, field in enumerate(fields):
        typename = field['type_name']
        if types.is_integer_type(typename):
            for row in data:
                val = row[col]
                if len(val) == 0:
                    row[col] = '0'  # 填充0
                elif val.find('.') >= 0:
                    num = int(round(float(val)))  # 这里是四舍五入
                    print('round integer', val, '-->', num)
                    row[col] = str(num)
        elif types.is_floating_type(typename):
            for row in data:
                if len(row[col]) == 0:
                    row[col] = '0'  # 填充0
        elif types.is_bool_type(typename):
            for row in data:
                b = strutil.str2bool(row[col])
                if b:
                    row[col] = 'true'
                else:
                    row[col] = 'false'
    return data


def convert_data(typename: str, val: str) -> str:
    if types.is_integer_type(typename):
        if len(val) == 0:
            val = '0'
        elif val.find('.') >= 0:
            num = int(round(float(val)))  # 这里是四舍五入
            print('round integer', val, '-->', num)
            val = str(num)
    elif types.is_floating_type(typename):
        if len(val) == 0:
            val = '0.0'
    elif types.is_bool_type(typename):
        b = strutil.str2bool(val)
        if b:
            val = 'true'
        else:
            val = 'false'
    return val


# # 把KV模式的不必要显示内容置空（类型和注释）
def blanking_kv_columns(table):
    for row in table:
        row[predef.PredefValueTypeColumn] = ''
        row[predef.PredefValueTypeColumn] = ''
    return table


# meta字段处理
def parse_meta(table):
    meta = {}
    for row in table:
        if len(row) >= 2:
            key = row[0].strip()
            value = row[1].strip()
            if len(key) > 0 and len(value) > 0:
                meta[key] = value
    return meta
