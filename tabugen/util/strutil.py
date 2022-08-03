"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import codecs
import datetime
import filecmp
import os
import random
import re
import shutil
import string
import tempfile
import typing
import unittest


def current_time() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


# 最长串的大小
def max_field_length(table: typing.Mapping, key: str, f: typing.Callable) -> int:
    max_len = 0
    for v in table:
        n = len(v[key])
        if f is not None:
            n = len(f(v[key]))
        if n > max_len:
            max_len = n
    return max_len


# 空格对齐
def pad_spaces(text: str, min_len: int) -> str:
    return text.ljust(min_len, ' ')


# snake case to camel case
def camel_case(s: str) -> str:
    if s == '':
        return s
    components = s.split('_')
    if len(components) == 1:
        return s[0].upper() + s[1:]
    return ''.join(x.title() for x in components)


# camel case to snake case
def camel_to_snake(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def escape_delimiter(ch: str) -> str:
    assert len(ch) == 1
    if ch == '\\':
        return '\\\\'
    elif ch == '\'':
        return '\\\''
    elif ch == '"':
        return '\\"'
    return ch


# 随机字符
def random_word(length: int) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


# 解析bool
def str2bool(text: str) -> bool:
    if len(text) == 0:
        return False
    return text.lower() in ['1', 't', 'ok', 'on', 'yes', 'true']


# a=1,b=2 => {a:1,b:2}
def parse_kv_to_dict(text: str) -> typing.Mapping:
    table = {}
    if len(text) == 0:
        return table
    for item in text.split(','):
        kv = item.split('=')
        assert len(kv) == 2, kv
        key = kv[0].strip()
        val = kv[1].strip()
        table[key] = val
    return table


# 最长共同前缀
def find_common_prefix(s1: str, s2: str) -> str:
    if len(s1) == 0 or len(s2) == 0:
        return ""
    prefix = s1
    if len(s2) < len(prefix):
        prefix = prefix[:len(s2)]
    if prefix == "":
        return ""
    for i in range(len(prefix)):
        if prefix[i] != s2[i]:
            prefix = prefix[:i]
            break
    return prefix


# 是否是相似的列（归为数组）
def is_vector_fields(prev: typing.Mapping, cur: typing.Mapping) -> bool:
    if prev["original_type_name"] != cur["original_type_name"]:
        return False

    name1 = prev['name']
    name2 = cur['name']
    prefix = find_common_prefix(name1, name2)
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


def is_last_char_digit(text: str) -> bool:
    if len(text) == 0:
        return False
    n = len(text)
    if 48 <= ord(text[n - 1]) <= 57:  # ['0', '9']
        return True
    return False


# 删除末尾的数字
def remove_suffix_number(text: str) -> str:
    n = len(text)
    if n == 0:
        return text
    while n >= 0:
        if 48 <= ord(text[n - 1]) <= 57:  # ['0', '9']
            n -= 1
        else:
            break
    return text[:n]


# 比较内容不相同时再写入文件
def save_content_if_not_same(filename: str, content: str, enc: str) -> bool:
    # first write content to a temporary file
    tmp_filename = 'tabugen_%s' % random_word(10)
    tmp_filename = os.path.join(tempfile.gettempdir(), tmp_filename)
    f = codecs.open(tmp_filename, 'w+', enc)
    f.writelines(content)
    f.close()

    # move to destination path if content not equal
    if os.path.isfile(filename) and filecmp.cmp(tmp_filename, filename):
        os.remove(tmp_filename)
        return False
    else:
        shutil.move(tmp_filename, filename)
        return True


# 对齐数据行
def pad_data_rows(fields, table):
    # pad empty row
    max_row_len = len(fields)
    for row in table:
        if len(row) > max_row_len:
            max_row_len = len(row)

    for row in table:
        for j in range(len(row), max_row_len):
            row.append('')
    return table


class TestUtils(unittest.TestCase):

    def test_remove_suffix_number(self):
        test_data = [
            ('', ''),
            ('1', ''),
            ('num1', 'num'),
            ('test01', 'test'),
        ]
        for pair in test_data:
            out = remove_suffix_number(pair[0])
            print(pair[0], '-->', out)
            self.assertEqual(pair[1], out)

    def test_parse_args(self):
        text = 'a=b,c=d,e=f'
        output = parse_kv_to_dict(text)
        print(output)
        self.assertEqual(output['a'], 'b')
        self.assertEqual(output['c'], 'd')
        self.assertEqual(output['e'], 'f')

    def test_camel_case(self):
        test_data = [
            ('', ''),
            ('a', 'A'),
            ('A', 'A'),
            ('Abc', 'Abc'),
            ('abc', 'Abc'),
            ('AbCd', 'AbCd'),
            ('ab_cd_ef_gh', 'AbCdEfGh'),
        ]
        for pair in test_data:
            out = camel_case(pair[0])
            print(out)
            self.assertEqual(pair[1], out)

    def test_common_prefix(self):
        test_data = [
            ("", "", ""),
            ("", "abc", ""),
            ("a", "a", "a"),
            ("abcdef", "abc", "abc"),
            ("abc", "abcdefg", "abc"),
            ("abcjklm", "abcdefg", "abc"),
        ]
        for item in test_data:
            out = find_common_prefix(item[0], item[1])
            print(out)
            self.assertEqual(out, item[2])


if __name__ == '__main__':
    unittest.main()
