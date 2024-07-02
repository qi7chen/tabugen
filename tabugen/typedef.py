# Copyright (C) 2024 ki7chen@github. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import unittest
from enum import Enum
from typing import Tuple


# 类型定义枚举
class Type(Enum):
    Unknown = 0
    Bool = 1
    Int8 = 2
    UInt8 = 3
    Int16 = 4
    UInt16 = 5
    Int32 = 8
    UInt32 = 9
    Int64 = 10
    UInt64 = 11
    Float32 = 14
    Float64 = 15
    String = 16
    Array = 17
    Map = 18


# text name of a type
name_types = {
    "bool": Type.Bool,
    "int8": Type.Int8,
    "uint8": Type.UInt8,
    "int16": Type.Int16,
    "uint16": Type.UInt16,
    "int32": Type.Int32,
    "uint32": Type.UInt32,
    "long": Type.Int64,
    "int64": Type.Int64,
    "uint64": Type.UInt64,
    "float32": Type.Float32,
    "float64": Type.Float64,
    "string": Type.String,
    "array": Type.Array,
    "map": Type.Map,
}

# 类型别名
alias = {
    'long': 'int64',
    'ulong': 'uint64',
    'int': 'int32',
    'uint': 'uint32',
    'float': 'float32',
    'double': 'float64',
    'str': 'string',
    'arr': 'array',
}

# non-primitive type names
composite_type_names = {
    "array": Type.Array,
    "map": Type.Map,
}

integer_types = [
    'int8', 'int16', 'int', 'int32', 'int64', 'long',
    'uint8', 'uint16', 'uint', 'uint32', 'uint64',
]

floating_types = ['float32', 'float64']


# get name of an integer type
def get_name_of_type(t: Type) -> str:
    for k, v in name_types.items():
        if v == t:
            return k
    return ''


def is_bool_type(typename: str) -> bool:
    return typename == 'bool'


# is integer type
def is_integer_type(typename: str) -> bool:
    return typename in integer_types


# is floating point
def is_floating_type(typename: str) -> bool:
    return typename in floating_types


# 基础类型
def is_primitive_type(name: str) -> bool:
    if is_integer_type(name) or is_floating_type(name):
        return True
    return name in ['bool', 'string']


# int[], string[]
def is_array_type(name: str) -> bool:
    if len(name) >= 5 and name.endswith('[]'):
        return is_primitive_type(name[:-2])
    return False


# <int, int>, <string, int>
def is_map_type(name: str) -> bool:
    if len(name) >= 5 and name.startswith('<') and name.endswith('>'):
        parts = name[1:-1].split(',')
        if len(parts) == 2:
            key_type = parts[0].strip()
            val_type = parts[1].strip()
            return is_primitive_type(key_type) and is_primitive_type(val_type)
    return False


# 是否正确的类型名称
def is_valid_type_name(name):
    if is_primitive_type(name):
        return True
    if is_array_type(name):
        return True
    if is_map_type(name):
        return True
    return False


# get type by name
def get_type_by_name(name: str) -> Type:
    typ = name_types.get(name, Type.Unknown)
    if typ != Type.Unknown:
        return typ
    if is_map_type(name):
        return Type.Map
    elif is_array_type(name):
        return Type.Array
    return Type.Unknown


def is_defined_type(name: str) -> bool:
    return get_type_by_name(name) != Type.Unknown


# 是否复合类型, 即 map/array
def is_composite_type(typename: str) -> str:
    if is_map_type(typename):
        return 'map'
    elif is_array_type(typename):
        return 'array'
    return ''


# 数组的元素类型, int[] => int
def array_element_type(typename: str) -> str:
    assert is_array_type(typename), typename
    return typename[:-2]


# map的元素类型,  <int, string> => (int, string)
def map_key_value_types(typename: str) -> Tuple:
    assert is_map_type(typename), typename
    parts = typename[1:-1].split(',')
    key_type = parts[0].strip()
    val_type = parts[1].strip()
    return key_type, val_type


def legacy_type_to_name(typen: int) -> str:
    if typen == 1:
        return 'int32'
    elif typen == 2:
        return 'string'
    elif typen == 3:
        return 'int32[]'
    elif typen == 4 or typen == 6:
        return '<int,int>'
    else:
        return 'string'


class TestTypes(unittest.TestCase):

    def test_is_primitive_type(self):
        test_cases = [
            ('', False),
            ('int', True),
            ('int8', True),
            ('float', True),
            ('float64', True),
            ('bool', True),
            ('string', True),
            ('map', False),
            ('array', False),
        ]
        for tc in test_cases:
            output = is_primitive_type(tc[0])
            self.assertEqual(output, tc[1])

    def test_get_type_by_name(self):
        test_cases = [
            ('', Type.Unknown),
            ('none', Type.Unknown),
            ('int', Type.Int32),
            ('int8', Type.Int8),
        ]
        for tc in test_cases:
            output = get_type_by_name(tc[0])
            self.assertEqual(output, tc[1])

    def test_array_element_type(self):
        test_cases = [
            ('int[]', 'int'),
            ('float[]', 'float'),
            ('bool[]', 'bool'),
            ('string[]', 'string'),
        ]
        for tc in test_cases:
            output = array_element_type(tc[0])
            self.assertEqual(output, tc[1])

    def test_map_key_value_types(self):
        test_cases = [
            ('<int,int>', 'int', 'int'),
            ('<int, string>', 'int', 'string'),
            ('<double, bool>', 'double', 'bool'),
        ]
        for tc in test_cases:
            output1, output2 = map_key_value_types(tc[0])
            self.assertEqual(output1, tc[1])
            self.assertEqual(output2, tc[2])


if __name__ == '__main__':
    unittest.main()
