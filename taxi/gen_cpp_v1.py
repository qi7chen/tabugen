# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import time
import unittest
import descriptor
import basegen
import predef
import util

# C++ code generator
class CppV1Generator(basegen.CodeGeneratorBase):

    def __init__(self):
        pass

    @staticmethod
    def name():
        return "cppv1"


    def get_instance_data_name(self, name):
        return '_instance_%s_data' % name.lower()


    def get_struct_keys(self, struct, keyname):
        if keyname not in struct['options']:
            return []

        key_tuples = []
        column_keys = struct['options'][keyname].split(',')
        assert len(column_keys) > 0, struct['name']

        for column in column_keys:
            idx, field = self.get_field_by_column_index(struct, int(column))
            typename = map_cpp_type(field['original_type_name'])
            name = field['name']
            key_tuples.append((typename, name))
        return key_tuples


    def gen_equal_stmt(self, prefix, struct, key):
        keys = self.get_struct_keys(struct, key)
        args = []
        for tpl in keys:
            args.append('%s%s == %s' % (prefix, tpl[1], tpl[1]))
        return ' && '.join(args)


    # array赋值
    def gen_field_array_assign_stmt(self, prefix, typename, name, row_name, delim):
        if delim == '':
            delim = predef.DefaultDelim1
        content = ''
        elemt_type = map_cpp_type(descriptor.array_element_type(typename))
        content += '            const vector<string>& array = Split(%s, "%s");\n' % (row_name, delim)
        content += '            for (size_t i = 0; i < array.size(); i++)\n'
        content += '            {\n'
        content += '                %s%s.push_back(to<%s>(array[i]));\n' % (prefix, name, elemt_type)
        content += '            }\n'
        return content


    # map赋值
    def gen_field_map_assgin_stmt(self, prefix, typename, name, row_name, delims):
        delim1 = predef.DefaultDelim1
        delim2 = predef.DefaultDelim2
        if delims != '':
            delist = [x.strip() for x in delims.split(',')]
            assert len(delist) == 2, delims
            delim1 = delist[0]
            delim2 = delist[1]
        k, v = descriptor.map_key_value_types(typename)
        key_type = map_cpp_type(k)
        val_type = map_cpp_type(v)
        content = ''
        content += '            const vector<string>& mapitems = Split(%s, "%s");\n' % (row_name, delim1)
        content += '            for (size_t i = 0; i < mapitems.size(); i++)\n'
        content += '            {\n'
        content += '                const vector<string>& kv = Split(mapitems[i], "%s");\n' % delim2
        content += '                BEATS_ASSERT(kv.size() == 2);\n'
        content += '                if(kv.size() == 2)\n'
        content += '                {\n'
        content += '                    BEATS_ASSERT(%s%s.count(kv[0]) == 0);\n' % (prefix, name)
        content += '                    %s%s[to<%s>(kv[0])] = to<%s>(kv[1]);\n' % (prefix, name, key_type, val_type)
        content += '                }\n'
        content += '            }\n'
        return content


    def gen_all_field_assign_stmt(self, struct):
        content = ''
        idx = 0
        delimeters = ''
        if predef.OptionDelimeters in struct['options']:
            delimeters = struct['options'][predef.OptionDelimeters]

        vec_names, vec_name = self.get_field_range(struct)
        vec_idx = 0
        for field in struct['fields']:
            origin_type = field['original_type_name']
            typename = map_cpp_type(origin_type)

            if typename != 'std::string' and field['name'] in vec_names:
                content += '        item.%s[%d] = %s;\n' % (vec_name, vec_idx, default_value_by_type(origin_type))

            content += '        if (!row[%d].empty())\n' % idx
            content += '        {\n'
            if origin_type.startswith('array'):
                content += self.gen_field_array_assign_stmt('item.', field['original_type_name'], field['name'],
                                                       'row[%d]' % idx, delimeters)
            elif origin_type.startswith('map'):
                content += self.gen_field_map_assgin_stmt('item.', field['original_type_name'], field['name'],
                                                     'row[%d]' % idx, delimeters)
            else:
                if field['name'] in vec_names:
                    content += '            item.%s[%d] = to<%s>(row[%d]);\n' % (vec_name, vec_idx, typename, idx)
                    vec_idx += 1
                else:
                    content += '            item.%s = to<%s>(row[%d]);\n' % (field['name'], typename, idx)
            content += '        }\n'
            idx += 1
        return content


    # 生成class定义结构
    def gen_cpp_struct_define(self, struct):
        content = '// %s\n' % struct['comment']
        content += 'struct %s \n{\n' % struct['name']
        fields = struct['fields']
        if struct['options'][predef.PredefParseKVMode]:
            fields = self.get_struct_kv_fields(struct)

        vec_done = False
        vec_names, vec_name = self.get_field_range(struct)

        max_name_len = util.max_field_length(fields, 'name', None)
        max_type_len = util.max_field_length(fields, 'original_type_name', map_cpp_type)

        for field in fields:
            typename = map_cpp_type(field['original_type_name'])
            assert typename != "", field['original_type_name']
            typename = util.pad_spaces(typename, max_type_len + 1)
            if field['name'] not in vec_names:
                name = name_with_default_value(field, typename)
                name = util.pad_spaces(name, max_name_len + 8)
                content += '    %s %s // %s\n' % (typename, name, field['comment'])
            elif not vec_done:
                name = '%s[%d];' % (vec_name, len(vec_names))
                name = util.pad_spaces(name, max_name_len + 8)
                content += '    %s %s // %s\n' % (typename, name, field['comment'])
                vec_done = True

        return content


    # class静态函数声明
    def gen_struct_method_declare(self, struct):
        content = ''
        content += '    static int Load();\n'
        if struct['options'][predef.PredefParseKVMode]:
            content += '    static const %s* Instance();\n' % struct['name']
            return content

        content += '    static const std::vector<%s>* GetData(); \n' % struct['name']
        get_keys = self.get_struct_keys(struct, predef.PredefGetMethodKeys)
        if len(get_keys) == 0:
            return content

        get_args = []
        for tpl in get_keys:
            typename = tpl[0]
            if not is_pod_type(typename):
                typename = 'const %s&' % typename
            get_args.append(typename + ' ' + tpl[1])

        content += '    static const %s* Get(%s);\n' % (struct['name'], ', '.join(get_args))

        if predef.PredefRangeMethodKeys in struct['options']:
            range_keys = self.get_struct_keys(struct, predef.PredefRangeMethodKeys)
            range_args = []
            for tpl in range_keys:
                typename = tpl[0]
                if not is_pod_type(typename):
                    typename = 'const %s&' % typename
                range_args.append(typename + ' ' + tpl[1])
            content += '    static std::vector<const %s*> GetRange(%s);\n' % (struct['name'], ', '.join(range_args))

        return content


    # 生成GetData()方法
    def gen_struct_data_method(self, struct):
        content = ''
        varname = self.get_instance_data_name(struct['name'])
        if struct['options']['parse-kv-mode']:
            content += 'const %s* %s::Instance()\n' % (struct['name'], struct['name'])
            content += '{\n'
            content += '    BEATS_ASSERT(%s != nullptr);\n' % varname
            content += '    return %s;\n' % varname
            content += '}\n\n'
        else:
            content += 'const std::vector<%s>* %s::GetData()\n' % (struct['name'], struct['name'])
            content += '{\n'
            content += '    BEATS_ASSERT(%s != nullptr);\n' % varname
            content += '    return %s;\n' % varname
            content += '}\n\n'
        return content


    # 生成Get()方法
    def gen_struct_get_method(self, struct):
        content = ''
        if struct['options'][predef.PredefParseKVMode]:
            return content

        keys = self.get_struct_keys(struct, predef.PredefGetMethodKeys)
        if len(keys) == 0:
            return content

        formal_param = []
        arg_names = []
        for tpl in keys:
            typename = tpl[0]
            if not is_pod_type(typename):
                typename = 'const %s&' % typename
            formal_param.append('%s %s' % (typename, tpl[1]))
            arg_names.append(tpl[1])

        content += 'const %s* %s::Get(%s)\n' % (struct['name'], struct['name'], ', '.join(formal_param))
        content += '{\n'
        content += '    const vector<%s>* dataptr = GetData();\n' % struct['name']
        content += '    BEATS_ASSERT(dataptr != nullptr && dataptr->size() > 0);\n'
        content += '    for (size_t i = 0; i < dataptr->size(); i++)\n'
        content += '    {\n'
        content += '        if (%s)\n' % self.gen_equal_stmt('dataptr->at(i).', struct, 'get-keys')
        content += '        {\n'
        content += '            return &dataptr->at(i);\n'
        content += '        }\n'
        content += '    }\n'
        content += '    BEATS_ASSERT(false, "%s.Get: no item found%s", %s);\n' % (
        struct['name'], ' {}' * len(arg_names), ', '.join(arg_names))
        content += '    return nullptr;\n'
        content += '}\n\n'
        return content


    # 生成GetRange()方法
    def gen_struct_range_method(self, struct):
        content = ''
        if struct['options'][predef.PredefParseKVMode]:
            return content

        if predef.PredefRangeMethodKeys not in struct['options']:
            return content

        keys = self.get_struct_keys(struct, predef.PredefRangeMethodKeys)
        assert len(keys) > 0

        formal_param = []
        params = []
        arg_names = []
        for tpl in keys:
            typename = tpl[0]
            if not is_pod_type(typename):
                typename = 'const %s&' % typename
            formal_param.append('%s %s' % (typename, tpl[1]))
            arg_names.append(tpl[1])

        content += 'std::vector<const %s*> %s::GetRange(%s)\n' % (
        struct['name'], struct['name'], ', '.join(formal_param))
        content += '{\n'
        content += '    const vector<%s>* dataptr = GetData();\n' % struct['name']
        content += '    std::vector<const %s*> range;\n' % struct['name']
        content += '    BEATS_ASSERT(dataptr != nullptr && dataptr->size() > 0);\n'
        content += '    for (size_t i = 0; i < dataptr->size(); i++)\n'
        content += '    {\n'
        content += '        if (%s)\n' % self.gen_equal_stmt('dataptr->at(i).', struct, 'range-keys')
        content += '        {\n'
        content += '            range.push_back(&dataptr->at(i));\n'
        content += '        }\n'
        content += '        else \n'
        content += '        {\n'
        content += '            if (!range.empty()) \n'
        content += '                break;\n'
        content += '        }\n'
        content += '    }\n'
        content += '    BEATS_ASSERT(!range.empty(), "%s.GetRange: no item found%s", %s);\n' % (
        struct['name'], ' {}' * len(arg_names), ', '.join(arg_names))
        content += '    return range;\n'
        content += '}\n\n'
        return content


    # KV模式的Load()方法
    def gen_kv_struct_load_method(self, struct):
        content = ''
        rows = struct['data-rows']
        keycol = struct['options']['key-column']
        valcol = struct['options']['value-column']
        typcol = int(struct['options']['value-type-column'])
        assert keycol > 0 and valcol > 0 and typcol > 0

        keyidx, keyfield = self.get_field_by_column_index(struct, keycol)
        validx, valfield = self.get_field_by_column_index(struct, valcol)
        typeidx, typefield = self.get_field_by_column_index(struct, typcol)

        delimeters = ''
        if predef.OptionDelimeters in struct['options']:
            delimeters = struct['options'][predef.OptionDelimeters]

        content = 'int %s::Load()\n' % struct['name']
        content += '{\n'
        content += '    const char* csvpath = "/csv/%s.csv";\n' % struct['name'].lower()
        content += '    %s* dataptr = BEATS_NEW(%s, "autogen", csvpath);\n' % (struct['name'], struct['name'])
        content += '    const vector<vector<string>>& rows = CResourceManager::GetInstance()->ReadCsvToRows(csvpath);\n'
        content += '    BEATS_ASSERT(rows.size() >= %d && rows[0].size() >= %d);\n' % (len(rows), validx)
        idx = 0
        for row in rows:
            name = rows[idx][keyidx].strip()
            origin_typename = rows[idx][typeidx].strip()
            typename = map_cpp_type(origin_typename)
            content += '    if (!rows[%d][%d].empty())\n' % (idx, validx)
            content += '    {\n'
            row_name = 'rows[%d][%d]' % (idx, validx)

            if typename == 'std::string':
                content += '        dataptr->%s = %s;\n' % (name, row_name)
            elif origin_typename.startswith('array'):
                content += self.gen_field_array_assign_stmt('dataptr->', origin_typename, name, row_name, delimeters)
            elif origin_typename.startswith('map'):
                content += self.gen_field_map_assgin_stmt('dataptr->', origin_typename, name, row_name, delimeters)
            else:
                content += '        dataptr->%s = to<%s>(%s);\n' % (name, typename, row_name)
            content += '    }\n'
            idx += 1
        varname = self.get_instance_data_name(struct['name'])
        content += '    BEATS_SAFE_DELETE(%s);\n' % varname
        content += '    %s = dataptr;\n' % varname
        content += '    return 0;\n'
        content += '}\n\n'
        return content


    # 生成Load()方法
    def gen_struct_load_method(self, struct):
        content = ''
        if struct['options']['parse-kv-mode']:
            return self.gen_kv_struct_load_method(struct)

        varname = self.get_instance_data_name(struct['name'])
        content += 'int %s::Load()\n' % struct['name']
        content += '{\n'
        content += '    const char* csvpath = "/csv/%s.csv";\n' % struct['name'].lower()
        content += '    vector<%s>* dataptr = BEATS_NEW(vector<%s>, "autogen", csvpath);\n' % (
        struct['name'], struct['name'])
        content += '    const vector<vector<string>>& rows = CResourceManager::GetInstance()->ReadCsvToRows(csvpath);\n'
        content += '    BEATS_ASSERT(rows.size() > 0);\n'
        content += '    for (size_t i = 0; i < rows.size(); i++)\n'
        content += '    {\n'
        content += '        const vector<string>& row = rows[i];\n'
        content += '        BEATS_ASSERT(row.size() >= %d);\n' % len(struct['fields'])
        content += '        %s item;\n' % struct['name']
        content += self.gen_all_field_assign_stmt(struct)
        content += '        dataptr->push_back(item);\n'
        content += '    }\n'
        content += '    BEATS_ASSERT(dataptr->size() > 0);\n'
        content += '    BEATS_SAFE_DELETE(%s);\n' % varname
        content += '    %s = dataptr;\n' % varname
        content += '    return 0;\n'
        content += '}\n\n'
        return content


    # class静态成员定义
    def gen_global_static_define(self, struct):
        content = ''
        content = ''
        varname = self.get_instance_data_name(struct['name'])
        if struct['options'][predef.PredefParseKVMode]:
            content += '    static %s* %s = nullptr;\n' % (struct['name'], varname)
        else:
            content += '    static std::vector<%s>* %s = nullptr;\n' % (struct['name'], varname)
        return content


    def gen_global_function(self, descriptors):
        content = ''
        clear_method_content = '// load all configurations\nvoid ClearAllAutogenConfig()\n{\n'
        load_method_content = '// clear all configuration\nvoid LoadAllAutogenConfig()\n{\n'
        for struct in descriptors:
            load_method_content += '    %s::Load();\n' % struct['name']
            clear_method_content += '    BEATS_SAFE_DELETE(%s);\n' % self.get_instance_data_name(struct['name'])
        load_method_content += '}\n\n'
        clear_method_content += '}\n\n'
        content += load_method_content
        content += clear_method_content
        return content


    def gen_cpp_header(self, struct):
        content = ''
        content += self.gen_cpp_struct_define(struct)
        content += '\n'
        content += self.gen_struct_method_declare(struct)
        content += '};\n\n'
        return content


    def gen_cpp_source(self, struct):
        content = ''
        content += self.gen_struct_data_method(struct)
        content += self.gen_struct_get_method(struct)
        content += self.gen_struct_range_method(struct)
        content += self.gen_struct_load_method(struct)
        return content


    def run(self, descriptors, args):
        params = util.parse_args(args)
        h_include_headers = [
            '#include <stdint.h>',
            '#include <string>',
            '#include <vector>',
        ]
        header_content = '// This file is auto-generated by taxi v%s, DO NOT EDIT!\n\n#pragma once\n\n' % util.version_string
        header_content += '\n'.join(h_include_headers) + '\n\n'
        header_content += '// Load all configurations\nvoid LoadAllAutogenConfig();\n\n'
        header_content += '// Cleanup all configurations\nvoid ClearAllAutogenConfig();\n\n'

        cpp_include_headers = [
            '#include "stdafx.h"',
            '#include <stddef.h>',
            '#include <memory>',
            '#include "AutogenConfig.h"',
            '#include "Utility/Conv.h"',
            '#include "Resource/ResourceManager.h"',
        ]
        cpp_content = '// This file is auto-generated by taxi v%s, DO NOT EDIT!\n\n' % util.version_string
        cpp_content += '\n'.join(cpp_include_headers) + '\n\n'
        cpp_content += 'using namespace std;\n\n'

        data_only = params.get(predef.OptionDataOnly, False)
        no_data = params.get(predef.OptionNoData, False)


        class_content = ''
        for struct in descriptors:
            self.setup_comment(struct)
            self.setup_key_value_mode(struct)
            if not no_data:
                self.write_data_rows(struct, params)
            if not data_only:
                header_content += self.gen_cpp_header(struct)
                class_content += self.gen_cpp_source(struct)

        if data_only:
            return

        static_define_content = 'namespace {\n'
        for struct in descriptors:
            static_define_content += self.gen_global_static_define(struct)
        static_define_content += '}\n\n'

        outdir = params.get(predef.OptionOutDataDir, '.')
        filename = outdir + '/AutogenConfig.h'
        util.compare_and_save_content(filename, header_content, 'gbk')
        print('wrote header file to', filename)

        cpp_content += static_define_content
        cpp_content += self.gen_global_function(descriptors)
        cpp_content += class_content
        filename = outdir + '/AutogenConfig.cpp'
        util.compare_and_save_content(filename, cpp_content, 'gbk')
        print('wrote source file to', filename)


# C++类型映射
def map_cpp_type(typ):
    type_mapping = {
        'bool':     'bool',
        'int8':     'int8_t',
        'uint8':    'uint8_t',
        'int16':    'int16_t',
        'uint16':   'uint16_t',
        'int':      'int',
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


# 为类型加上默认值
def name_with_default_value(field, typename):
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


def default_value_by_type(typename):
    if typename == 'bool':
        return 'false'
    elif descriptor.is_integer_type(typename):
        return '0'
    elif descriptor.is_floating_type(typename):
        return '0.0'
    return ''


def is_pod_type(typ):
    assert len(typ.strip()) > 0
    return not typ.startswith('std::')  # std::string, std::vector, std::map