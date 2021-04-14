# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import re
import random
import string
import shutil
import tempfile
import filecmp
import codecs
import datetime
import unittest


def current_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


# 最长串的大小
def max_field_length(table, key, f):
    max_len = 0
    for v in table:
        n = len(v[key])
        if f is not None:
            n = len(f(v[key]))
        if n > max_len:
            max_len = n
    return max_len


# 空格对齐
def pad_spaces(text, min_len):
    if len(text) < min_len:
        for n in range(min_len - len(text)):
            text += ' '
    return text


# snake case to camel case
def camel_case(s):
    if s == '':
        return s
    components = s.split('_')
    if len(components) == 1:
        return s[0].upper() + s[1:]
    return ''.join(x.title() for x in components)


# camel case to snake case
def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def escape_delimiter(ch):
    assert len(ch) == 1
    if ch == '\\':
        return '\\\\'
    elif ch == '\'':
        return '\\\''
    elif ch == '"':
        return '\\"'
    return ch

# 随机字符
def random_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


# a=1,b=2 => {a:1,b:2}
def parse_kv_to_obj(text):
    table = {}
    if len(text) == 0:
        return table
    for item in text.split(','):
        kv = item.split('=')
        assert len(kv) == 2, kv
        table[kv[0].strip()] = kv[1].strip()
    return table


# 最长共同前缀
def find_common_prefix(s1, s2):
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


# 是否全部是空字符串
def is_row_empty(row):
    for v in row:
        v = v.strip()
        if len(v) > 0:
            return False
    return True


# 是否是相似的列（归为数组）
def is_vector_fields(prev, cur):
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


# 删除末尾的数字
def remove_suffix_number(text):
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
def save_content_if_not_same(filename, content, enc):
    # first write content to a temporary file
    tmp_filename = '%s/taksi_%s' % (tempfile.gettempdir(), random_word(10))
    f = codecs.open(tmp_filename, 'w', enc)
    f.writelines(content)
    f.close()

    # move to destination path if content not equal
    if os.path.isfile(filename) and filecmp.cmp(tmp_filename, filename):
        os.remove(tmp_filename)
        return False
    else:
        shutil.move(tmp_filename, filename)
        return True


# 从路径种搜索所有excel文件
def enum_files(self, rootdir, ignore_check):
    files = []
    for dirpath, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            if filename.endswith(".xlsx"):
                files.append(dirpath + os.sep + filename)
    filenames = []
    for filename in files:
        if ignore_check is not None:
            if not ignore_check(filename):
                filename = os.path.abspath(filename)
                filenames.append(filename)
    return filenames


# 对齐数据行
def pad_data_rows(rows, fields):
    # pad empty row
    max_row_len = len(fields)
    for row in rows:
        if len(row) > max_row_len:
            max_row_len = len(row)

    for row in rows:
        for j in range(len(row), max_row_len):
            row.append("")
    return rows


# array和map分隔符  "|=" --> ['|', '=']
def to_sep_delimiters(array_delim, map_delims):
    assert isinstance(array_delim, str) and len(array_delim) == 1, array_delim
    assert len(map_delims) == 2, map_delims
    delim1 = array_delim.strip()
    if delim1 == '\\':
        delim1 = '\\\\'

    delim2 = [map_delims[0].strip(), map_delims[1].strip()]
    if delim2[0] == '\\':
        delim2[0] = '\\\\'
    if delim2[1] == '\\':
        delim2[1] = '\\\\'
    return (delim1, delim2)


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
        output = parse_kv_to_obj(text)
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
