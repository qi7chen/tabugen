"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

from typing import Mapping

import tabugen.typedef as types
import tabugen.util.strutil as strutil


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
        'float': 'float',
        'float32': 'float',
        'float64': 'double',
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
        name = strutil.remove_suffix_number(name)
    if typename == 'bool':
        return '%s = false;' % name
    elif types.is_integer_type(field['type_name']):
        return '%s = 0;' % name
    elif types.is_floating_type(field['type_name']):
        return '%s = 0.0;' % name
    else:
        return '%s;' % name


# C++字符串解析
def map_cpp_parse_expr(typ: str, param: str) -> str:
    mapping = {
        'bool': 'ParseBool',
        'int8': 'ParseInt8',
        'uint8': 'ParseUInt8',
        'int16': 'ParseInt16',
        'uint16': 'ParseUInt16',
        'int': 'ParseInt32',
        'uint': 'ParseUInt32',
        'int32': 'ParseInt32',
        'uint32': 'ParseUInt32',
        'int64': 'ParseInt64',
        'uint64': 'ParseUInt64',
        'float': 'ParseFloat',
        'float32': 'ParseFloat',
        'float64': 'ParseDouble',
        'enum': 'ParseInt32',
        'string': 'StripWhitespace',
    }
    return '%s(%s)' % (mapping[typ], param)


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
        'float': 'float32',
        'float32': 'float32',
        'float64': 'float64',
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
        'float': 'float32',
        'float32': 'float32',
        'float64': 'float64',
        'string': 'string',
        'bytes': '[]byte',
        'datetime': 'time.Time',
    }
    return go_type_mapping[typ]


# Go字符串解析
def map_go_parse_expr(typ: str, param: str) -> str:
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
        'float': 'parseF64',
        'float32': 'parseF32',
        'float64': 'parseF64',
        'enum': 'parseI32',
        'string': 'strings.TrimSpace',
    }
    return '%s(%s)' % (mapping[typ], param)


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
        'float': 'float',
        'float32': 'float',
        'float64': 'double',
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
def map_cs_parse_expr(typ: str, param: str) -> str:
    if typ == 'string':
        return param + '.Trim()'

    mapping = {
        'bool': 'bool.Parse',
        'int8': 'sbyte.Parse',
        'uint8': 'byte.Parse',
        'int16': 'short.Parse',
        'uint16': 'ushort.Parse',
        'int': 'int.Parse',
        'uint': 'uint.Parse',
        'int32': 'int.Parse',
        'uint32': 'uint.Parse',
        'int64': 'long.Parse',
        'uint64': 'ulong.Parse',
        'float': 'float.Parse',
        'float32': 'float.Parse',
        'float64': 'float.Parse',
        'enum': 'int.Parse',
    }
    return '%s(%s)' % (mapping[typ], param)


# C#类型默认值
def name_with_default_cs_value(field: Mapping, typename: str, remove_suffix_num: bool) -> str:
    typename = typename.strip()
    name = field['name']
    if remove_suffix_num:
        name = strutil.remove_suffix_number(name)
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
        'float': 'float',
        'float32': 'float',
        'float64': 'double',
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
        name = strutil.remove_suffix_number(name)
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
def map_java_parse_expr(typ: str, param: str) -> str:
    if typ == 'string':
        return param + '.trim()'

    mapping = {
        'bool': 'Boolean.parseBoolean',
        'int8': 'Byte.parseByte',
        'uint8': 'Byte.parseByte',
        'int16': 'Short.parseShort',
        'uint16': 'Short.parseShort',
        'int': 'Integer.parseInt',
        'uint': 'Integer.parseInt',
        'int32': 'Integer.parseInt',
        'uint32': 'Integer.parseInt',
        'int64': 'Long.parseLong',
        'uint64': 'Long.parseLong',
        'float': 'Float.parseFloat',
        'float32': 'Float.parseFloat',
        'float64': 'Double.parseDouble',
        'enum': 'Integer.parseInt',
    }
    return '%s(%s)' % (mapping[typ], param)

