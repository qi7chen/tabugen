"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import sys

import tabugen.predef as predef
import tabugen.typedef as types
import tabugen.util.strutil as strutil


# 删除table的某一列
def remove_table_column(table, column: int):
    for col in range(len(table)):
        row = table[col]
        if column < len(row):
            row = row[:column] + row[column + 1:]
            table[col] = row
    return table


# 删除空白列(在中间的列）
def remove_table_empty_columns(table, field_row: int):
    header = table[field_row]
    col = len(header)
    while col > 0:
        col -= 1
        field = header[col]
        # header为空白的列需要删除，以#或者//开头的列表示注释，也需要删除
        if len(field) == 0 or field.startswith('#') or field.startswith('//'):
            table = remove_table_column(table, col)
    return table


# 删除首部和尾部连续的空列
def trim_empty_columns(table, field_row: int):
    header = table[field_row]
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


# 删除全部空白的行和列
def table_remove_empty(table, field_row: int):
    table = trim_empty_columns(table, field_row)

    # 删除header中的注释和空白
    header = table[field_row]
    for col, filed in enumerate(header):
        field = filed.strip()
        idx = field.find('\n')
        if idx > 0:
            field = field[:idx]
        header[col] = field

    # 根据header，删除被忽略和空白的列
    return remove_table_empty_columns(table, field_row)


# 解析格式：A_XXX
def parse_head_field(text):
    i = text.find('_')
    if i > 0:
        text = text[i+1:]
    return text


# 检查字段名是否有重复
def check_duplicate_header_fields(table):
    header = table[predef.PredefFieldNameRow]  # 第一行是头部
    keys = {}
    for text in header:
        name = parse_head_field(text)
        idx = name.find('\n')
        if idx > 0:
            name = name[:idx]
        if name in keys:
            raise RuntimeError('duplicate key %s ' % name)
        keys[name] = True


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
    header = table[predef.PredefFieldNameRow]
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
    for col, field in enumerate(struct['fields']):
        if field['name'] in names:
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
                    row[col] = '1'
                else:
                    row[col] = '0'
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
            val = '1'
        else:
            val = '0'
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


# 解析出内嵌字段， 如：foo[0], bar[0], foo[1], bar[1]
def parse_inner_fields(struct):
    fields = struct['fields']
    start = 0
    end = 0
    gap = 0
    for i, field in enumerate(fields):
        if field['name'].endswith('[0]'):
            start = i
            break

    for i in range(start, len(fields)):
        field_name = fields[i]['name']
        if len(field_name) <= 3 or field_name[-1] != ']' or field_name[-3] != '[':
            return {}
        if field_name.endswith('[1]') and field_name[:-3] == fields[start]['name'][:-3]:
            gap = i - start
            end = i
            break

    while end + 1 < len(fields):
        field_name = fields[end+1]['name']
        if len(field_name) > 3 and field_name[-1] == ']' or field_name[-3] == '[':
            end += 1

    for s in range(gap):
        loop = (end - start + 1) // gap
        idx = -1
        name = ''
        for n in range(loop):
            field_name = fields[start + n*gap+s]['name']
            if len(field_name) <= 3 or field_name[-1] != ']' or field_name[-3] != '[':
                return {}
            i = int(field_name[-2])
            if i - idx != 1:
                return {}
            idx = i
            if name == '':
                name = field_name[:-3]
            elif field_name[:-3] != name:
                return {}

    if 0 < start < end and gap > 0:
        return {
            'start': start,
            'end': end,
            'step': gap,
        }
    return {}


def remove_field_suffix(name: str) -> str:
    if len(name) > 3 and name[-1] == ']' or name[-3] == '[':
        return name[:-3]


def find_col_by_name(row, name: str) -> int:
    for col, val in enumerate(row):
        if name == val:
            return col
    return -1
