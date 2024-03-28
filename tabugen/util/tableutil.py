# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import sys
import unittest
import tabugen.predef as predef
import tabugen.typedef as types
import tabugen.util.helper as helper

max_int64 = 9223372036854775807
min_int64 = -9223372036854775808
max_float32 = float('3.4e+38')
min_float32 = float('1.4e-45')


def split_field_name(name: str):
    kind = ''
    type_name = ''
    i = name.find('_')
    if i <= 0:
        return kind, type_name, name
    j = name.find('_', i + 1)
    if j > 0:
        kind = name[:i].upper()
        type_name = name[i + 1: j]
        return kind, type_name.lower(), name[j + 1:]
    else:
        type_name = name[: i + 1]
        return kind, type_name.lower(), name[i + 1:]


# 这一行是否是类型定义
def is_type_row(row):
    for text in row:
        if not types.is_valid_type_name(text):
            return False
    return len(row) > 0


def parse_elem_type(arr):
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


def parse_array_elem_type(text):
    arr = text.split(helper.Delim1)
    return parse_elem_type(arr)


def parse_map_elem_type(text):
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
def infer_field_type(table, start_row: int, col: int):
    parsed = ''
    for n in range(start_row, len(table)):
        type_name = parse_elem_type(table[n][col])
        if parsed == '':
            parsed = type_name
        if parsed != type_name:
            return 'string'
    return parsed


def infer_field_array_type(table, start_row: int, col: int):
    elem_type = ''
    for n in range(start_row, len(table)):
        type_name = parse_array_elem_type(table[n][col])
        if elem_type == '':
            elem_type = type_name
        if elem_type != type_name:
            return 'string[]'
    return elem_type + '[]'


def infer_field_map_type(table, start_row: int, col: int):
    elem_ktype = ''
    elem_vtype = ''
    for n in range(start_row, len(table)):
        t1, t2 = parse_map_elem_type(table[n][col])
        if elem_ktype == '' and elem_vtype == '':
            elem_ktype = t1
            elem_vtype = t2
        if t1 != elem_ktype or t2 != elem_vtype:
            return '<string,string>'
    return '<%s,%s>' % (elem_ktype, elem_vtype)


# 删除table的某一列
def remove_table_column(table, column: int):
    for col in range(len(table)):
        row = table[col]
        if column < len(row):
            row = row[:column] + row[column + 1:]
            table[col] = row
    return table


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


# 删除首部和尾部连续的空列
def trim_empty_columns(table):
    header = table[predef.PredefFieldNameRow]
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
def table_remove_empty(table):
    table = trim_empty_columns(table)

    # 删除header中的注释和空白
    header = table[predef.PredefFieldNameRow]
    for col, filed in enumerate(header):
        field = filed.strip()
        idx = field.find('\n')
        if idx > 0:
            field = field[:idx]
        header[col] = field

    # 根据header，删除被忽略和空白的列
    return remove_table_empty_columns(table)


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
    if predef.PredefParseKVMode in struct['options']:
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
                    print('%s field %s round integer %s -> %s' % (struct['name'], field['name'], val,  num))
                    row[col] = str(num)
        elif types.is_floating_type(typename):
            for row in data:
                if len(row[col]) == 0:
                    row[col] = '0'  # 填充0
        elif types.is_bool_type(typename):
            for row in data:
                b = helper.str2bool(row[col])
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
        b = helper.str2bool(val)
        if b:
            val = '1'
        else:
            val = '0'
    return val


# 是否是相似的列（归为数组）
def is_vector_fields(prev, cur) -> bool:
    if prev["original_type_name"] != cur["original_type_name"]:
        return False

    name1 = prev['name']
    name2 = cur['name']
    prefix = helper.find_common_prefix(name1, name2)
    if prefix == "":
        return False
    if len(prefix) == len(name1) or len(prefix) == len(name2):
        return False
    s1 = name1[len(prefix)]
    s2 = name2[len(prefix)]
    if s1.isdigit() and s2.isdigit():
        n1 = int(s1)
        n2 = int(s2)
        return n1 + 1 == n2
    return False


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
        field_name = fields[end + 1]['name']
        if len(field_name) > 3 and field_name[-1] == ']' or field_name[-3] == '[':
            end += 1

    for s in range(gap):
        loop = (end - start + 1) // gap
        idx = -1
        name = ''
        for n in range(loop):
            field_name = fields[start + n * gap + s]['name']
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


def is_kv_table(table, legacy=False):
    header = table[predef.PredefFieldNameRow]
    if len(header) < 3:
        return False
    if predef.PredefKVKeyName not in header:
        return False
    if predef.PredefKVValueName not in header:
        return False
    for col, name in enumerate(header):
        if name == predef.PredefKVKeyName:  # name列是否全是名称定义
            for n in range(1, len(table)):
                if parse_elem_type(table[n][col]) != 'string':
                    return False
        elif name == predef.PredefKVTypeName and not legacy:  # type列是否全是类型定义
            for n in range(1, len(table)):
                if not types.is_valid_type_name(table[n][col]):
                    return False
    return True


class TestTypes(unittest.TestCase):
    def test_is_type_row(self):
        self.assertTrue(is_type_row(['int', 'string', 'long']))
        self.assertTrue(is_type_row(['int', 'str', 'float']))
        self.assertTrue(is_type_row(['int', 'str', 'bool']))
        self.assertFalse(is_type_row(['int', 'str', 'boolean']))


if __name__ == '__main__':
    unittest.main()
