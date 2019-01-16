# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import descriptor

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
    abs_type = descriptor.is_abstract_type(typ)
    if abs_type is None:
        return type_mapping[typ]

    if abs_type == 'array':
        t = descriptor.array_element_type(typ)
        elem_type = type_mapping[t]
        return 'std::vector<%s>' % elem_type
    elif abs_type == 'map':
        k, v = descriptor.map_key_value_types(typ)
        key_type = type_mapping[k]
        value_type = type_mapping[v]
        return 'std::map<%s, %s>' % (key_type, value_type)
    assert False, typ


# POD类型
def is_cpp_pod_type(typ):
    assert len(typ.strip()) > 0
    return not typ.startswith('std::')  # std::string, std::vector, std::map


# C++为类型加上默认值
def name_with_default_cpp_value(field, typename):
    typename = typename.strip()
    line = ''
    if typename == 'bool':
        line = '%s = false;' % field['name']
    elif descriptor.is_integer_type(field['type_name']):
        line = '%s = 0;' % field['name']
    elif descriptor.is_floating_type(field['type_name']):
        line = '%s = 0.0;' % field['name']
    else:
        line = '%s;' % field['name']
    assert len(line) > 0
    return line


# C++默认值
def default_value_by_cpp_type(typename):
    if typename == 'bool':
        return 'false'
    elif descriptor.is_integer_type(typename):
        return '0'
    elif descriptor.is_floating_type(typename):
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
    abs_type = descriptor.is_abstract_type(typ)
    if abs_type is None:
        return type_mapping[typ]

    if abs_type == 'array':
        t = descriptor.array_element_type(typ)
        elem_type = type_mapping[t]
        return '[]%s' % elem_type
    elif abs_type == 'map':
        k, v = descriptor.map_key_value_types(typ)
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
    abs_type = descriptor.is_abstract_type(typ)
    if abs_type is None:
        return type_mapping[typ]

    if abs_type == 'array':
        t = descriptor.array_element_type(typ)
        elem_type = type_mapping[t]
        return 'List<%s>' % elem_type
    elif abs_type == 'map':
        k, v = descriptor.map_key_value_types(typ)
        key_type = type_mapping[k]
        value_type = type_mapping[v]
        return 'Dictionary<%s, %s>' % (key_type, value_type)
    assert False, typ


# C#默认值
def name_with_default_cs_value(field, typename):
    typename = typename.strip()
    line = ''
    if typename == 'bool':
        line = '%s = false;' % field['name']
    elif typename == 'string':
        line = '%s = "";' % field['name']
    elif descriptor.is_integer_type(field['type_name']):
        line = '%s = 0;' % field['name']
    elif descriptor.is_floating_type(field['type_name']):
        line = '%s = 0.0f;' % field['name']
    elif typename.startswith('List'):
        line = '%s = new %s();' % (field['name'], typename)
    elif typename.startswith('Dictionary'):
        line = '%s = new %s();' % (field['name'], typename)
    else:
        line = '%s;' % field['name']
    assert len(line) > 0
    return line

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
    abs_type = descriptor.is_abstract_type(typ)
    if abs_type is None:
        return type_mapping[typ]
    if abs_type == 'array':
        t = descriptor.array_element_type(typ)
        elem_type = type_mapping[t]
        return '%s[]' % elem_type
    elif abs_type == 'map':
        k, v = descriptor.map_key_value_types(typ)
        key_type = java_box_type(type_mapping[k])
        value_type = java_box_type(type_mapping[v])
        return 'HashMap<%s,%s>' % (key_type, value_type)
    assert False, typ

# java默认值
def name_with_default_java_value(field, typename):
    typename = typename.strip()
    # print(typename)
    if typename == 'boolean':
        return '%s = false;' % field['name']
    elif typename == 'String':
        return '%s = "";' % field['name']
    elif descriptor.is_integer_type(field['type_name']):
        return '%s = 0;' % field['name']
    elif descriptor.is_floating_type(field['type_name']):
        return '%s = 0.0f;' % field['name']
    elif typename.startswith('HashMap'):
        return '%s = new %s();' % (field['name'], typename)
    else:
        return '%s = null;' % field['name']

def is_java_primitive_type(typ):
    table = ['boolean', 'byte', 'short', 'int', 'long', 'float', 'double', 'decimal']
    return typ in table