# Copyright (C) 2018-present qi7chen@github. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import sys
import unittest
from argparse import Namespace
import tabugen.predef as predef
import tabugen.typedef as types
import tabugen.util.helper as helper
from tabugen.structs import Struct, StructField

max_int64 = 9223372036854775807
min_int64 = -9223372036854775808
max_float32 = float('3.4e+38')
min_float32 = float('1.4e-45')


# 拆分字段名，A_INT_Level -> A, int, level
def split_field_name(name: str) -> tuple[str, str, str]:
    kind = ''
    type_name = ''
    first = name.find('_')
    if first <= 0:
        return kind, type_name, name
    second = name.find('_', first + 1)
    if second > 0:
        kind = name[:first].upper()
        type_name = name[first + 1: second]
        return kind, type_name.lower(), name[second + 1:]
    else:
        type_name = name[: first]
        return kind, type_name.lower(), name[first + 1:]


def row_find_field_name(row: list[str], name: str) -> int:
    for i, text in enumerate(row):
        kind, typename, field_name = split_field_name(text)
        if field_name == name:
            return i
    return -1


# 这一行是否是类型定义
def is_type_row(row: list[str]) -> bool:
    for text in row:
        if not types.is_valid_type_name(text):
            return False
    return len(row) > 0


def parse_cell_type(text: str) -> str:
    try:
        int(text)
        return 'int'
    except ValueError:
        try:
            float(text)
            return 'float'
        except ValueError:
            pass
    return 'string'


def parse_elem_type(arr: list[str]) -> str:
    try:
        a = [int(x) for x in arr]
        if len(a) > 0:
            for n in a:
                if n <= min_int64 or n >= max_int64:
                    return 'int64'
            return 'int'
    except ValueError:
        try:
            a = [float(x) for x in arr]
            if len(a) > 0:
                for n in a:
                    if n <= min_float32 or n >= max_float32:
                        return 'double'
                return 'float'
        except ValueError:
            pass
    return 'string'


def parse_array_elem_type(text: str) -> str:
    arr = text.split(helper.Delim1)
    return parse_elem_type(arr)


def parse_map_elem_type(text: str) -> tuple[str, str]:
    keys = []
    values = []
    parts = text.split(helper.Delim1)
    for part in parts:
        kv = part.split(helper.Delim2)
        if len(kv) == 2:
            keys.append(kv[0])
            values.append(kv[1])
    key_type = parse_elem_type(keys)
    value_type = parse_elem_type(values)
    return key_type, value_type


# 根据内容解析字段类型
def infer_field_type(table: list[list[str]], start_row: int, col: int):
    parsed = ''
    for n in range(start_row, len(table)):
        type_name = parse_cell_type(table[n][col])
        if parsed == '':
            parsed = type_name
        if parsed != type_name:
            return 'string'
    return parsed


def infer_field_array_type(table: list[list[str]], start_row: int, col: int):
    elem_type = ''
    for n in range(start_row, min(len(table), 20)):
        type_name = parse_array_elem_type(table[n][col])
        if elem_type == '':
            elem_type = type_name
        if elem_type != type_name:
            return 'string[]'
    return elem_type + '[]'


def infer_field_map_type(rows: list[list[str]], start_row: int, col: int):
    elem_ktype = ''
    elem_vtype = ''
    for n in range(start_row, min(len(rows), 20)):
        t1, t2 = parse_map_elem_type(rows[n][col])
        if elem_ktype == '' and elem_vtype == '':
            elem_ktype = t1
            elem_vtype = t2
        if t1 != elem_ktype or t2 != elem_vtype:
            return '<string,string>'
    return '<%s,%s>' % (elem_ktype, elem_vtype)


# 删除table的某一列
def remove_table_column(rows: list[list[str]], column: int):
    for col in range(len(rows)):
        row = rows[col]
        if column < len(row):
            row = row[:column] + row[column + 1:]
            rows[col] = row
    return rows


# 删除首部和尾部连续的空列
def trim_empty_columns(rows: list[list[str]]):
    header = rows[predef.PredefFieldNameRow]
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
        for i in range(len(rows)):
            rows[i] = rows[i][start:end]
    return rows


# 删除空白列(在中间的列）
def remove_table_empty_columns(table):
    header = table[predef.PredefFieldNameRow]
    col = len(header)
    while col > 0:
        col -= 1
        field = header[col]
        # header为空白的列需要删除，以#或者//开头的列表示注释，也需要删除
        if len(field) == 0 or field.startswith('#') or field.startswith('//'):
            table = remove_table_column(table, col)
    return table


# 删除header中的注释列
def table_remove_comment_columns(columns: list[int], rows: list[list[str]]):
    if len(columns) == 0:
        return []
    if len(rows) == 0:
        return []

    first_row = rows[0]
    col = len(first_row)
    while col > 0:
        col -= 1
        if col not in columns:
            rows = remove_table_column(rows, col)
    return rows


# 解析格式：A_XXX
def parse_head_field(text):
    i = text.find('_')
    if i > 0:
        text = text[i + 1:]
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
def is_all_row_field_value_unique(rows: list[list[str]], col: int) -> (bool, int, int):
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
def validate_unique_column(struct: Struct, rows: list[list[str]]) -> list[list[str]]:
    if predef.PredefParseKVMode in struct.options:
        return rows

    if predef.OptionUniqueColumns not in struct.options:
        return rows

    names = struct.options[predef.OptionUniqueColumns]
    if len(names) == 0:
        return rows

    for col, field in enumerate(struct.fields):
        if field.name in names:
            (is_unique, row_line, exist_line) = is_all_row_field_value_unique(rows, col)
            if not is_unique:
                print('duplicate field %s value found, row %d and row %d' % (field.name, exist_line, row_line))
                sys.exit(1)
    return rows


# 处理一下数据
# 1，配置的数值类型如果为空，默认填充0
# 2，如果配置的类型是整数，但实际有浮点，需要转换成整数
def convert_table_data(struct: Struct, rows: list[list[str]]) -> list[list[str]]:
    for col, field in enumerate(struct.raw_fields):
        typename = field.type_name
        if types.is_integer_type(typename):
            for i, row in enumerate(rows):
                val = row[col]
                if len(val) == 0:
                    row[col] = '0'  # 填充0
                elif val.find('.') >= 0:
                    num = int(round(float(val)))  # 这里是四舍五入
                    print('%s field %s round integer %s -> %s' % (struct.name, field.name, val,  num))
                    rows[i][col] = str(num)
        elif types.is_floating_type(typename):
            for i, row in enumerate(rows):
                if len(row[col]) == 0:
                    rows[i][col] = '0'  # 填充0
        elif types.is_bool_type(typename):
            for i, row in enumerate(rows):
                b = helper.str2bool(row[col])
                rows[i][col] = '1' if b else '0'
    return rows


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
        b = helper.str2bool(val)
        if b:
            val = '1'
        else:
            val = '0'
    return val


def remove_field_suffix(name: str) -> str:
    if len(name) <= 3:
        return name
    if name[-1] == ']' and name[-3] == '[':
        return name[:-3]
    return name


def find_col_by_name(row, name: str) -> int:
    for col, val in enumerate(row):
        if name == val:
            return col
    return -1


def legacy_kv_type(ty: int) -> str:
    if ty == 1:
        return 'int'
    elif ty == 2:
        return 'string'
    elif ty == 3:
        return 'int[]'
    elif ty == 4 or ty == 6:
        return '<int, int>'
    elif ty == 5:
        return 'float'
    return ''


def is_valid_kv_name(name: str) -> bool:
    if len(name) == 0 or name[0].isdigit():
        return False
    if ' ' in name or '-' in name or '.' in name:
        return False
    return True


# 包含 [Key, Type, Value] 三个字段名
def is_kv_table(table: list[list[str]], legacy=True) -> bool:
    header = table[predef.PredefFieldNameRow]
    if len(header) < 3:
        return False

    key_idx = row_find_field_name(header, predef.PredefKVKeyName)
    if key_idx < 0:
        return False
    val_idx = row_find_field_name(header, predef.PredefKVValueName)
    if val_idx < 0:
        return False
    type_idx = row_find_field_name(header, predef.PredefKVTypeName)
    if type_idx < 0 and not legacy:
        return False

    for n in range(1, min(len(table), 20)):
        row = table[n]
        name = row[key_idx].strip()
        if not is_valid_kv_name(name):
            return False

        # 没有类型定义列默认为int64
        if type_idx < 0:
            try:
                if len(row[val_idx]) > 0:
                    int(row[val_idx])
            except ValueError:
                return False
        else:
            type_name = row[type_idx]
            if type_name.isdigit():
                type_name = legacy_kv_type(int(type_name))
            if not types.is_valid_type_name(type_name):
                return False

    return True


def parse_kv_fields(struct: Struct, legacy, mapper1, mapper2) -> list[StructField]:
    key_idx = struct.get_column_index(predef.PredefKVKeyName)
    assert key_idx >= 0
    type_idx = struct.get_column_index(predef.PredefKVTypeName)
    comment_idx = struct.get_kv_comment_col()

    fields = []
    for row in struct.data_rows:
        varname = row[key_idx]
        typename = 'int'
        if type_idx >= 0:
            typename = row[type_idx]
        if varname == '' or typename == '':
            continue

        field = StructField()
        if legacy and typename.isdigit():
            typename = legacy_kv_type(int(typename))

        field.origin_type_name = typename
        if typename in types.alias:
            field.type_name = types.alias[typename]
        else:
            field.type_name = field.origin_type_name
        field.lang_type_name = mapper1(typename)
        field.name = varname
        field.camel_case_name = varname
        field.name_defval = mapper2(field)
        if comment_idx >= 0:
            comment = row[comment_idx].strip()
            comment = comment.replace('\n', ' ')
            comment = comment.replace('//', '')
            field.comment = comment
        fields.append(field)
    return fields


class TestTypes(unittest.TestCase):
    def test_is_type_row(self):
        self.assertTrue(is_type_row(['int', 'string', 'long']))
        self.assertTrue(is_type_row(['int', 'str', 'float']))
        self.assertTrue(is_type_row(['int', 'str', 'bool']))
        self.assertFalse(is_type_row(['int', 'str', 'boolean']))


if __name__ == '__main__':
    unittest.main()
