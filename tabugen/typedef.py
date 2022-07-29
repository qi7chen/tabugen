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


# 基础类型
def is_primitive_type(name: str) -> bool:
    found = False
    for k, v in type_names.items():
        if v == name:
            found = True
            break

    if not found:
        return False

    for s in abstract_type_names:
        if s == name:
            return False
    return True


# get type by name
def get_type_by_name(name: str) -> Type:
    for k, v in abstract_type_names.items():
        if name.find(k) >= 0:
            return v
    for k, v in type_names.items():
        if v == name:
            return k
    return Type.Unknown


def is_defined_type(name: str) -> bool:
    return get_type_by_name(name) != Type.Unknown


def is_bool_type(typename: str) -> bool:
    return typename == 'bool'


# is integer type
def is_integer_type(typename: str) -> bool:
    return typename in integer_types


# is floating point
def is_floating_type(typename: str) -> bool:
    return typename in floating_types


# 是否抽象类型, map, array
def is_abstract_type(typename: str) -> str:
    if typename.startswith('map<'):
        return 'map'
    elif typename.startswith('array<'):
        return 'array'
    return ''


# array<int> --> int
def array_element_type(typename: str) -> str:
    assert typename.startswith('array<'), typename
    return typename[6:-1]


# map<int, string> --> int, string
def map_key_value_types(typename: str) -> Tuple:
    keytype = ''
    valtype = ''
    assert typename.startswith('map<'), typename
    typename = typename[4:]
    for v in type_names.values():
        if typename.startswith(v):
            keytype = v
            break
    typename = typename[len(keytype) + 1:]
    for v in type_names.values():
        if typename.startswith(v):
            valtype = v
            break

    assert len(keytype) > 0 and len(valtype) > 0
    return keytype, valtype


class TestTypes(unittest.TestCase):

    def test_primitive_type(self):
        test_data = [
            ('int', True),
            ('map', False),
            ('', False),
        ]
        for pair in test_data:
            out = is_primitive_type(pair[0])
            print(out)


if __name__ == '__main__':
    unittest.main()
