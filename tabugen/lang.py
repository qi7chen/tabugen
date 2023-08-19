"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

from typing import Mapping

import tabugen.typedef as types
import tabugen.util.tableutil as tableutil


# C++类型映射
def map_cpp_type(typ: str) -> str:
    type_mapping = {
        'bool': 'bool',
        'int8': 'int8_t',
        'uint8': 'uint8_t',
        'int16': 'int16_t',
        'uint16': 'uint16_t',
        'int': 'int',
        'uint': 'uint32_t',
        'int32': 'int32_t',
        'uint32': 'uint32_t',
        'int64': 'int64_t',
        'uint64': 'uint64_t',
        'float32': 'float',
        'float64': 'double',
        'float': 'double',
        'enum': 'enum',
        'string': 'std::string',
    }
    abs_type = types.is_abstract_type(typ)
    if abs_type == '':
        return type_mapping[typ]

    if abs_type == 'array':
        t = types.array_element_type(typ)
        elem_type = type_mapping[t]
        return 'std::vector<%s>' % elem_type
    elif abs_type == 'map':
        k, v = types.map_key_value_types(typ)
        key_type = type_mapping[k]
        value_type = type_mapping[v]
        return 'std::unordered_map<%s, %s>' % (key_type, value_type)
    assert False, typ


# C++ POD类型
def is_cpp_pod_type(typ: str) -> bool:
    assert len(typ.strip()) > 0
    return not typ.startswith('std::')  # std::string, std::vector, std::unordered_map


# C++为类型加上默认值
def name_with_default_cpp_value(field: Mapping, typename: str, remove_suffix_num: bool) -> str:
    typename = typename.strip()
    name = field['name']
    if remove_suffix_num:
        name = tableutil.remove_field_suffix(name)
    if typename == 'bool':
        return '%s = false;' % name
    elif types.is_integer_type(field['type_name']):
        return '%s = 0;' % name
    elif types.is_floating_type(field['type_name']):
        return '%s = 0.0;' % name
    else:
        return '%s;' % name


# C++类型默认值
def default_value_by_cpp_type(typename: str) -> str:
    if typename == 'bool':
        return 'false'
    elif types.is_integer_type(typename):
        return '0'
    elif types.is_floating_type(typename):
        return '0.0'
    return ''


# Go类型映射
def map_go_type(typ: str) -> str:
    type_mapping = {
        'bool': 'bool',
        'int8': 'int8',
        'uint8': 'uint8',
        'int16': 'int16',
        'uint16': 'uint16',
        'int': 'int',
        'uint': 'uint',
        'int32': 'int32',
        'uint32': 'uint32',
        'int64': 'int64',
        'uint64': 'uint64',
        'float32': 'float32',
        'float64': 'float64',
        'float': 'float64',
        'enum': 'int',
        'string': 'string',
    }
    abs_type = types.is_abstract_type(typ)
    if abs_type == '':
        return type_mapping[typ]

    if abs_type == 'array':
        t = types.array_element_type(typ)
        elem_type = type_mapping[t]
        return '[]%s' % elem_type
    elif abs_type == 'map':
        k, v = types.map_key_value_types(typ)
        key_type = type_mapping[k]
        value_type = type_mapping[v]
        return 'map[%s]%s' % (key_type, value_type)
    assert False, typ


# Go类型
def map_go_raw_type(typ: str) -> str:
    go_type_mapping = {
        'bool': 'bool',
        'int8': 'int8',
        'uint8': 'uint8',
        'int16': 'int16',
        'uint16': 'uint16',
        'int': 'int',
        'int32': 'int32',
        'uint32': 'uint32',
        'int64': 'int64',
        'uint64': 'uint64',
        'float32': 'float32',
        'float64': 'float64',
        'float': 'float64',
        'string': 'string',
        'bytes': '[]byte',
        'datetime': 'time.Time',
    }
    return go_type_mapping[typ]


# Go字符串解析
def map_go_parse_func(typ: str) -> str:
    mapping = {
        'bool': 'parseBool',
        'int8': 'parseI8',
        'uint8': 'parseU8',
        'int16': 'parseI16',
        'uint16': 'parseU16',
        'int': 'parseInt',
        'uint': 'parseUint',
        'int32': 'parseI32',
        'uint32': 'parseU32',
        'int64': 'parseI64',
        'uint64': 'parseU64',
        'float32': 'parseF32',
        'float64': 'parseF64',
        'float': 'parseF64',
        'enum': 'parseI32',
        'string': 'strings.TrimSpace',
    }
    return mapping[typ]


# C#类型映射
def map_cs_type(typ: str) -> str:
    type_mapping = {
        'bool': 'bool',
        'int8': 'sbyte',
        'uint8': 'byte',
        'int16': 'short',
        'uint16': 'ushort',
        'int': 'int',
        'uint': 'uint',
        'int32': 'int',
        'uint32': 'uint',
        'int64': 'long',
        'uint64': 'ulong',
        'float32': 'float',
        'float64': 'double',
        'float': 'double',
        'enum': 'int',
        'string': 'string',
    }
    abs_type = types.is_abstract_type(typ)
    if abs_type == '':
        return type_mapping[typ]

    if abs_type == 'array':
        t = types.array_element_type(typ)
        elem_type = type_mapping[t]
        return '%s[]' % elem_type
    elif abs_type == 'map':
        k, v = types.map_key_value_types(typ)
        key_type = type_mapping[k]
        value_type = type_mapping[v]
        return 'Dictionary<%s, %s>' % (key_type, value_type)
    # print(typ)
    assert False, typ


# C#字符串解析
def map_cs_parse_func(typ: str) -> str:
    mapping = {
        'bool': 'Conv.ParseBool',
        'int8': 'Conv.ParseByte',
        'uint8': 'Conv.ParseUByte',
        'int16': 'Conv.ParseShort',
        'uint16': 'Conv.ParseUShort',
        'int': 'Conv.ParseInt',
        'uint': 'Conv.ParseUInt',
        'int32': 'Conv.ParseInt',
        'uint32': 'Conv.ParseUInt',
        'int64': 'Conv.ParseLong',
        'uint64': 'Conv.ParseULong',
        'float32': 'Conv.ParseFloat',
        'float64': 'Conv.ParseDouble',
        'float': 'Conv.ParseDouble',
        'enum': 'Conv.ParseInt',
    }
    return mapping[typ]


# C#类型默认值
def name_with_default_cs_value(field: Mapping, typename: str, remove_suffix_num: bool) -> str:
    typename = typename.strip()
    name = field['name']
    if remove_suffix_num:
        name = tableutil.remove_field_suffix(name)
    return '%s { get; set; }' % name


# java装箱类型
def java_box_type(typ: str) -> str:
    table = {
        'boolean': 'Boolean',
        'byte': 'Byte',
        'short': 'Short',
        'int': 'Integer',
        'long': 'Long',
        'float': 'Float',
        'double': 'Double',
        'String': 'String',
    }
    return table[typ]


# java类型映射
def map_java_type(typ: str) -> str:
    type_mapping = {
        'bool': 'boolean',
        'int8': 'byte',
        'uint8': 'byte',
        'int16': 'short',
        'uint16': 'short',
        'int': 'int',
        'uint': 'int',
        'int32': 'int',
        'uint32': 'int',
        'int64': 'long',
        'uint64': 'long',
        'float32': 'float',
        'float64': 'double',
        'float': 'double',
        'enum': 'int',
        'string': 'String',
    }
    abs_type = types.is_abstract_type(typ)
    if abs_type == '':
        return type_mapping[typ]
    if abs_type == 'array':
        t = types.array_element_type(typ)
        elem_type = type_mapping[t]
        return '%s[]' % elem_type
    elif abs_type == 'map':
        k, v = types.map_key_value_types(typ)
        key_type = java_box_type(type_mapping[k])
        value_type = java_box_type(type_mapping[v])
        return 'Map<%s,%s>' % (key_type, value_type)
    assert False, typ


# java类型默认值
def name_with_default_java_value(field: Mapping, typename: str, remove_suffix_num: bool) -> str:
    typename = typename.strip()
    # print(typename)
    name = field['name']
    if remove_suffix_num:
        name = tableutil.remove_field_suffix(name)
    if typename.startswith('bool'):
        return '%s = false;' % name
    elif typename == 'String':
        return '%s = "";' % name
    elif types.is_integer_type(field['type_name']):
        return '%s = 0;' % name
    elif types.is_floating_type(field['type_name']):
        return '%s = 0.0f;' % name
    else:
        return '%s = null;' % name


def is_java_primitive_type(typ: str) -> bool:
    table = ['boolean', 'byte', 'short', 'int', 'long', 'float', 'double', 'decimal']
    return typ in table


# java字符串解析
def map_java_parse_func(typ: str) -> str:
    mapping = {
        'bool': 'Conv.parseBool',
        'int8': 'Conv.parseByte',
        'uint8': 'Conv.parseByte',
        'int16': 'Conv.parseShort',
        'uint16': 'Conv.parseShort',
        'int': 'Conv.parseInt',
        'uint': 'Conv.parseInt',
        'int32': 'Conv.parseInt',
        'uint32': 'Conv.parseInt',
        'int64': 'Conv.parseLong',
        'uint64': 'Conv.parseLong',
        'float32': 'Conv.parseFloat',
        'float64': 'Conv.parseDouble',
        'float': 'Conv.parseDouble',
        'enum': 'Conv.parseInt',
    }
    return mapping[typ]


def map_java_parse_array_func(typ: str) -> str:
    mapping = {
        'bool': 'Conv.parseBoolArray',
        'byte': 'Conv.parseByteArray',
        'short': 'Conv.parseShortArray',
        'int': 'Conv.parseIntArray',
        'long': 'Conv.parseLongArray',
        'float': 'Conv.parseFloatArray',
        'double': 'Conv.parseDoubleArray',
    }
    return mapping[typ]
