# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import unittest

# type enum
Type_Unknown = 0
Type_Nil = 1
Type_Bool = 2
Type_Int8 = 3
Type_Uint8 = 4
Type_Int16 = 5
Type_Uint16 = 6
Type_Int = 7
Type_Uint = 8
Type_Int32 = 9
Type_Uint32 = 10
Type_Int64 = 11
Type_Uint64 = 12
Type_Float = 13
Type_Float32 = 14
Type_Float64 = 15
Type_String = 16
Type_Enum = 17
Type_Bytes = 18
Type_DateTime = 19
Type_Array = 20
Type_Map = 21
Type_Any = 22

# text name of a type
type_names = {
    Type_Nil:      "nil",
    Type_Bool:     "bool",
    Type_Int8:     "int8",
    Type_Uint8:    "uint8",
    Type_Int16:    "int16",
    Type_Uint16:   "uint16",
    Type_Int:      "int",
    Type_Uint:     "uint32",
    Type_Int32:    "int32",
    Type_Uint32:   "uint32",
    Type_Int64:    "int64",
    Type_Uint64:   "uint64",
    Type_Float:    "float",
    Type_Float32:  "float32",
    Type_Float64:  "float64",
    Type_String:   "string",
    Type_Enum:     "enum",
    Type_Bytes:    "bytes",
    Type_DateTime: "datetime",
    Type_Array:    "array",
    Type_Map:      "map",
    Type_Any:      "any",
}

# non-primitive type names
abstract_type_names = {
    "array": Type_Array,
    "map":   Type_Map,
    "any":   Type_Any,
}

interger_types = ['int8', 'uint8', 'int16', 'uint16', 'int', 'uint','int32', 'uint32', 'int64', 'uint64', 'enum']
floating_types = ['float', 'float32', 'float64']


# get name of an integer type
def get_name_of_type(t):
    return type_names[t]


# 基础类型
def is_primitive_type(name):
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


# get integer type by name
def get_type_by_name(name):
    for k, v in abstract_type_names.items():
        if name.find(k) >= 0:
            return v
    for k, v in type_names.items():
        if v == name:
            return k
    return Type_Unknown


# is integer type
def is_integer_type(typ):
    return typ in interger_types


# is floating point
def is_floating_type(typ):
    return typ in floating_types


# 是否抽象类型, map, array
def is_abstract_type(typename):
    if typename.startswith('map<'):
        return 'map'
    elif typename.startswith('array<'):
        return 'array'
    return None


# array<int> --> int
def array_element_type(typename):
    assert typename.startswith('array<'), typename
    return typename[6:-1]


# map<int, string> --> int, string
def map_key_value_types(typename):
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


class TestTypeNames(unittest.TestCase):

    def test_is_primitive_type(self):
        test_data = [
            ('int', True),
            ('map', False),
            ('', False),
        ]
        for pair in test_data:
            out = is_primitive_type(pair[0])
            print(out)
            self.assertEqual(pair[1], out)


if __name__ == '__main__':
    unittest.main()
