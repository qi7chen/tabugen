"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import sys
import typing

import tabugen.predef as predef
import tabugen.typedef as types


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
def is_all_row_field_value_unique(rows, index: int) -> typing.Tuple:
    all_set = {}
    for i, row in rows:
        if len(row[index]) > 0:
            value = row[index]
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
    for _, field in struct['fields']:
        if field['name'] in names:
            idx = field['column_index'] - 1
            (is_unique, row_line, exist_line) = is_all_row_field_value_unique(rows, idx)
            if not is_unique:
                print('duplicate field %s value found, row %d and row %d' % (field['name'], exist_line, row_line))
                sys.exit(1)
    return rows


# 只保留enable的field
def blanking_disabled_columns(struct, table):
    for field in struct['fields']:
        if not field['enable']:
            for row in table:
                idx = field['column_index'] - 1
                row[idx] = ''
    return table


# 如果配置的类型是整数，但实际有浮点，需要转换成整数
def convert_table_data(struct, table):
    fields = struct['fields']
    data = table[predef.PredefDataStartRow:]
    for col, field in enumerate(fields):
        typename = field['type_name']
        if types.is_integer_type(typename):
            for row in data:
                val = row[col]
                if len(val) > 0 and val.find('.') >= 0:
                    num = int(round(float(val)))  # 这里是四舍五入
                    print('round integer', val, '-->', num)
                    row[col] = str(num)
    return table


# # 把KV模式的不必要显示内容置空（类型和注释）
def blanking_kv_columns(table):
    for row in table:
        row[predef.PredefValueTypeColumn] = ''
        row[predef.PredefValueTypeColumn] = ''
    return table


# 是否是KeyValue模式
def set_meta_kv_mode(table, meta):
    meta[predef.PredefParseKVMode] = False

    if len(table) == 0:
        return

    # 所有列长度为4
    header = table[0]
    if len(header) != predef.PredefCommentColumn + 1:
        return

    # 第一行都是
    all_head_is_type = True
    for name in header:
        if not types.is_defined_type(name):
            all_head_is_type = False
            break
    if all_head_is_type:
        return

    # 检查类型列
    for row in table:
        name = row[predef.PredefValueTypeColumn]
        if not types.is_defined_type(name):
            return

    meta[predef.PredefParseKVMode] = True


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
