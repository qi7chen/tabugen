"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import unittest
import tabugen.util.strutil as strutil


# 根据'column_index'查找一个字段
def get_field_by_column_index(struct, column_idx: int):
    assert column_idx > 0
    idx = 0
    for field in struct["fields"]:
        if field["column_index"] == column_idx:
            return idx, field
        idx += 1
    # print(struct['fields'])
    assert False, column_idx


# 获取字段
def get_struct_keys(struct, keyname: str, keymapping):
    if keyname not in struct['options']:
        return []

    key_tuples = []
    column_keys = struct['options'][keyname].split(',')
    assert len(column_keys) > 0, struct['name']

    for column in column_keys:
        idx, field = get_field_by_column_index(struct, int(column))
        typename = keymapping(field['original_type_name'])
        name = field['name']
        key_tuples.append((typename, name))
    return key_tuples


# 是否连续的字段: [XXX1, XXX2]这样的格式
def is_consecutive_fields(fields, i: int, j: int) -> bool:
    name1 = fields[i]['name']
    name2 = fields[j]['name']

    # 以数字结尾
    if not strutil.is_last_char_digit(name1) or not strutil.is_last_char_digit(name2):
        return False

    prefix = strutil.find_common_prefix(name1, name2)
    if len(prefix) == 0:
        return False

    n1 = int(name1[len(prefix):])
    n2 = int(name2[len(prefix):])
    return n2 == n1 + 1


def parse_fields_range(fields, a: int, b: int):
    gap = b - a

    # 区间内是否都是连续字段
    for i in range(gap):
        if not is_consecutive_fields(fields, a+i, b+i):
            return

    # 判断长度
    pos = b
    end = b + gap
    while end < len(fields):
        if is_consecutive_fields(fields, pos, end):
            end += gap
            pos = end

    start = a
    result = {
        'start': start,
        'end': end,
        'step': gap,
        'range': [],
    }
    while start < end:
        vec = []
        for k in range(gap):
            vec.append(fields[start]['column_index'])
            start += 1
        result['range'].append(vec)
    return result


# 解析出内嵌字段
def parse_inner_fields(struct):
    fields = struct['fields']
    for i, field in enumerate(fields):
        j = 0
        while j < i:
            if is_consecutive_fields(fields, j, i):
                return parse_fields_range(fields, j, i)
            j += 1
    return {}


class TestUtils(unittest.TestCase):

    def test_check_consecutive_fields(self):
        fields = [{'name': 'test1'}, {'name': 'test2'}]
        is_consecutive_fields(fields, 0, 1)


if __name__ == '__main__':
    unittest.main()
