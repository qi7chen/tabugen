# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import unittest


version_string = '1.0.1'


# snake case to camel case
def camel_case(s):
    if s == '':
        return s
    components = s.split('_')
    if len(components) == 1:
        return s[0].upper() + s[1:]
    return ''.join(x.title() for x in components)


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