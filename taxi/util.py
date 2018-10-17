# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import random
import string
import shutil
import tempfile
import filecmp
import codecs
import unittest


version_string = '1.0.1'


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


def random_word(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


def parse_args(text):
    assert len(text) > 0, text
    map = {}
    for item in text.split(','):
        kv = item.split('=')
        assert len(kv) == 2, kv
        map[kv[0].strip()] = kv[1].strip()
    return map


ignoreExcelPattern = [
    '~$',
    '-TNP-',
    ' - 副本',
]

def is_ignored_filename(filename):
    for text in ignoreExcelPattern:
        if filename.find(text) >= 0:
            return True
    return False


# longest common prefix
def common_prefix(s1, s2):
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
def is_vector_fields(prev, cur):
    if prev["original_type_name"] == cur["original_type_name"]:
        s1 = prev['name']
        s2 = cur['name']
        prefix = common_prefix(s1, s2)
        if prefix == "":
            return False
        try:
            n1 = int(s1[len(prefix):])
            n2 = int(s1[len(prefix):])
            return n1 + 1 == n2
        except Exception:
            return False

    return False


def read_sheet_to_csv(sheet):
    rows = []
    for i, sheet_row in enumerate(sheet.rows):
        row = []
        for j, cell in enumerate(sheet_row):
            text = ''
            if cell.value is not None:
                text = str(cell.value)
            row.append(text.strip())
        rows.append(row)
    return rows


# compare file content and save to file if not equal
def compare_and_save_file(filename, content, enc):
    # first write content to a temporary file
    tmp_filename = '%s/taxi_%s' % (tempfile.gettempdir(), random_word(10))
    f = codecs.open(tmp_filename, 'w', enc)
    f.writelines(content)
    f.close()

    # move to destination path if content not equal
    if os.path.isfile(filename) and filecmp.cmp(tmp_filename, filename):
        print('file content not modified', filename)
    else:
        shutil.move(tmp_filename, filename)

    
class TestUtils(unittest.TestCase):

    def test_parse_args(self):
        text = 'a=b,c=d,e=f'
        output = parse_args(text)
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
            out = common_prefix(item[0], item[1])
            print(out)
            self.assertEqual(out, item[2])

if __name__ == '__main__':
    unittest.main()