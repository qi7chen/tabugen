# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import tabugen.typedef as types


# C++类型映射
def map_cpp_type(typ):
    type_mapping = {
        'bool':     'bool',
        'int8':     'int8_t',
        'uint8':    'uint8_t',
        'int16':    'int16_t',
        'uint16':   'uint16_t',
        'int':      'int',
        'uint':     'uint32_t',
        'int32':    'int32_t',
        'uint32':   'uint32_t',
        'int64':    'int64_t',
        'uint64':   'uint64_t',
        'float':    'float',
        'float32':  'float',
        'float64':  'double',
        'enum':     'enum',
        'string':   'std::string',
    }
    abs_type = types.is_abstract_type(typ)
    if abs_type is None:
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


# POD类型
def is_cpp_pod_type(typ):
    assert len(typ.strip()) > 0
    return not typ.startswith('std::')  # std::string, std::vector, std::map


# C++为类型加上默认值
def name_with_default_cpp_value(field, typename):
    typename = typename.strip()
    if typename == 'bool':
        return '%s = false;' % field['name']
    elif types.is_integer_type(field['type_name']):
        return '%s = 0;' % field['name']
    elif types.is_floating_type(field['type_name']):
        return '%s = 0.0;' % field['name']
    else:
        return '%s;' % field['name']


# C++默认值
def default_value_by_cpp_type(typename):
    if typename == 'bool':
        return 'false'
    elif types.is_integer_type(typename):
        return '0'
    elif types.is_floating_type(typename):
        return '0.0'
    return ''


# Go类型映射
def map_go_type(typ):
    type_mapping = {
        'bool':     'bool',
        'int8':     'int8',
        'uint8':    'uint8',
        'int16':    'int16',
        'uint16':   'uint16',
        'int':      'int',
        'uint':      'uint',
        'int32':    'int32',
        'uint32':   'uint32',
        'int64':    'int64',
        'uint64':   'uint64',
        'float':    'float32',
        'float32':  'float32',
        'float64':  'float64',
        'enum':     'int',
        'string':   'string',
    }
    abs_type = types.is_abstract_type(typ)
    if abs_type is None:
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
def map_go_raw_type(typ):
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


def map_go_reflect_type(typ):
    mapping = {
        'bool':     'reflect.Bool',
        'int8':     'reflect.Int8',
        'uint8':    'reflect.Uint8',
        'int16':    'reflect.Int16',
        'uint16':   'reflect.Uint16',
        'int':      'reflect.Int',
        'uint':      'reflect.Uint',
        'int32':    'reflect.Int32',
        'uint32':   'reflect.Uint32',
        'int64':    'reflect.Int64',
        'uint64':   'reflect.Uint64',
        'float':    'reflect.Float32',
        'float32':  'reflect.Float32',
        'float64':  'reflect.Float64',
        'enum':     'reflect.Int',
        'string':   'reflect.String',
    }
    return mapping[typ]


# C#类型映射
def map_cs_type(typ):
    type_mapping = {
        'bool':     'bool',
        'int8':     'sbyte',
        'uint8':    'byte',
        'int16':    'short',
        'uint16':   'ushort',
        'int':      'int',
        'uint':     'uint',
        'int32':    'int',
        'uint32':   'uint',
        'int64':    'long',
        'uint64':   'ulong',
        'float':    'float',
        'float32':  'float',
        'float64':  'double',
        'enum':     'int',
        'string':   'string',
    }
    abs_type = types.is_abstract_type(typ)
    if abs_type is None:
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
    assert False, typ


# C#默认值
def name_with_default_cs_value(field, typename):
    typename = typename.strip()
    if typename == 'bool':
        return '%s = false;' % field['name']
    elif typename == 'string':
        return '%s = "";' % field['name']
    elif types.is_integer_type(field['type_name']):
        return '%s = 0;' % field['name']
    elif types.is_floating_type(field['type_name']):
        return '%s = 0.0f;' % field['name']
    else:
        return '%s = null;' % field['name']


# java装箱类型
def java_box_type(typ):
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


# java类型
def map_java_type(typ):
    type_mapping = {
        'bool':     'boolean',
        'int8':     'byte',
        'uint8':    'byte',
        'int16':    'short',
        'uint16':   'short',
        'int':      'int',
        'uint':     'int',
        'int32':    'int',
        'uint32':   'int',
        'int64':    'long',
        'uint64':   'long',
        'float':    'float',
        'float32':  'float',
        'float64':  'double',
        'enum':     'int',
        'string':   'String',
    }
    abs_type = types.is_abstract_type(typ)
    if abs_type is None:
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


# java默认值
def name_with_default_java_value(field, typename):
    typename = typename.strip()
    # print(typename)
    if typename == 'boolean':
        return '%s = false;' % field['name']
    elif typename == 'String':
        return '%s = "";' % field['name']
    elif types.is_integer_type(field['type_name']):
        return '%s = 0;' % field['name']
    elif types.is_floating_type(field['type_name']):
        return '%s = 0.0f;' % field['name']
    elif typename.startswith("List"):
        return '%s = new ArrayList<>();' % field['name']
    elif typename.startswith('Map'):
        return '%s = new HashMap<>();' % field['name']
    else:
        return '%s = null;' % field['name']


def is_java_primitive_type(typ):
    table = ['boolean', 'byte', 'short', 'int', 'long', 'float', 'double', 'decimal']
    return typ in table