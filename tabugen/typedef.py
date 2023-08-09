"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import unittest
from enum import Enum
from typing import Tuple


# 类型定义枚举
class Type(Enum):
    Unknown = 0
    Nil = 1
    Bool = 2
    Int8 = 3
    UInt8 = 4
    Int16 = 5
    UInt16 = 6
    Int = 7
    UInt = 8
    Int32 = 9
    UInt32 = 10
    Int64 = 11
    UInt64 = 12
    Float = 13
    Float32 = 14
    Float64 = 15
    String = 16
    Enum2 = 17
    Bytes = 18
    Array = 19
    DateTime = 20
    Map = 21
    Any = 22


# text name of a type
type_names = {
    Type.Nil: "nil",
    Type.Bool: "bool",
    Type.Int8: "int8",
    Type.UInt8: "uint8",
    Type.Int16: "int16",
    Type.UInt16: "uint16",
    Type.Int: "int",
    Type.UInt: "uint32",
    Type.Int32: "int32",
    Type.UInt32: "uint32",
    Type.Int64: "int64",
    Type.UInt64: "uint64",
    Type.Float: "float",
    Type.Float32: "float32",
    Type.Float64: "float64",
    Type.String: "string",
    Type.Enum2: "enum",
    Type.Bytes: "bytes",
    Type.DateTime: "datetime",
    Type.Array: "array",
    Type.Map: "map",
    Type.Any: "any",
}


def name_of_type():
    d = {}
    for k in type_names:
        v = type_names[k]
        d[v] = k
    return d


name_types = name_of_type()

# non-primitive type names
abstract_type_names = {
    "array": Type.Array,
    "map": Type.Map,
    "any": Type.Any,
}

integer_types = ['int8', 'uint8', 'int16', 'uint16', 'int', 'uint', 'int32', 'uint32', 'int64', 'uint64', 'enum']
floating_types = ['float', 'float32', 'float64']


# get name of an integer type
def get_name_of_type(t: Type) -> str:
    return type_names[t]


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


# get type by name
def get_type_by_name(name: str) -> Type:
    typ = name_types.get(name, Type.Unknown)
    if typ != Type.Unknown:
        return typ
    for k, v in abstract_type_names.items():
        if name.find(k) >= 0:
            return v
    return Type.Unknown


def is_defined_type(name: str) -> bool:
    return get_type_by_name(name) != Type.Unknown


# 是否抽象类型, map, array
def is_abstract_type(typename: str) -> str:
    if typename.startswith('<') and typename.endswith('>'):
        return 'map'
    elif typename.endswith('[]'):
        return 'array'
    return ''


# array<int> --> int
def array_element_type(typename: str) -> str:
    assert typename.endswith('[]'), typename
    return typename[:-2]


# map<int, string> --> int, string
def map_key_value_types(typename: str) -> Tuple:
    assert typename.startswith('<') and typename.endswith('>'), typename
    parts = typename[1:-1].split(',')
    assert len(parts) == 2, typename
    key_type = parts[0].strip()
    val_type = parts[1].strip()
    assert key_type in name_types, typename
    assert val_type in name_types, typename
    return key_type, val_type


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
            ('nil', False),
        ]
        for tc in test_cases:
            output = is_primitive_type(tc[0])
            self.assertEqual(output, tc[1])

    def test_get_type_by_name(self):
        test_cases = [
            ('', Type.Unknown),
            ('none', Type.Unknown),
            ('int', Type.Int),
            ('int8', Type.Int8),
            ('nil', Type.Nil),
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
            output = get_type_by_name(tc[0])
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
