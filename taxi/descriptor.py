# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import unittest

Type_Unknown = 0
Type_Nil = 1
Type_Bool = 2
Type_Int8 = 3
Type_Uint8 = 4
Type_Int16 = 5
Type_Uint16 = 6
Type_Int = 7
Type_Int32 = 8
Type_Uint32 = 9
Type_Int64 = 10
Type_Uint64 = 11
Type_Float = 12
Type_Float32 = 13
Type_Float64 = 14
Type_String = 15
Type_Enum = 16
Type_Bytes = 17
Type_DateTime = 18
Type_Array = 19
Type_Map = 20
Type_Any = 21

type_names = {
    Type_Nil:      "nil",
    Type_Bool:     "bool",
	Type_Int8:     "int8",
	Type_Uint8:    "uint8",
	Type_Int16:    "int16",
	Type_Uint16:   "uint16",
	Type_Int:      "int",
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

abstract_type_names = {
	"array": Type_Array,
	"map":   Type_Map,
	"any":   Type_Any,
}


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
    table = ['int8', 'uint8', 'int16', 'uint16', 'int', 'int32', 'uint32', 'int64', 'uint64', ]
    return typ in table


# is floating point
def is_floating_type(typ):
    return typ == 'float' or typ == 'float32' or typ == 'float64'


# 是否抽象类型, map, array
def is_abstract_type(typename):
    if typename.startswith('map<'):
        return 'map'
    elif typename.startswith('array<'):
        return 'array'


# array<int> --> int
def array_element_type(typename):
    assert typename.startswith('array<'), typename
    return typename[6:-1]


# map<int, string> --> int, string
def map_key_value_types(typename):
    assert typename.startswith('map<'), typename
    names = [x.strip() for x in typename[4:-1].split(',')]
    assert len(names) == 2
    return names[0], names[1]


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
