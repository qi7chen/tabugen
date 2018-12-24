# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import unittest
import descriptor
import basegen
import predef
import util


# C++ code generator
class CppV1Generator(basegen.CodeGeneratorBase):
    TAB_SPACE = '    '

    def __init__(self):
        pass

    @staticmethod
    def name():
        return "cpp-v1"

    def get_instance_data_name(self, name):
        return '_instance_%s' % name.lower()

    def gen_equal_stmt(self, prefix, struct, key):
        keys = self.get_struct_keys(struct, key, map_cpp_type)
        args = []
        for tpl in keys:
            args.append('%s%s == %s' % (prefix, tpl[1], tpl[1]))
        return ' && '.join(args)

    # array赋值
    def gen_field_array_assign_stmt(self, prefix, typename, name, row_name, array_delim, tabs):
        assert len(array_delim) == 1
        array_delim = array_delim.strip()
        if array_delim == '\\':
            array_delim = '\\\\'

        space = self.TAB_SPACE * tabs
        elemt_type = map_cpp_type(descriptor.array_element_type(typename))
        content = ''
        content += '%sconst auto& array = Split(%s, "%s");\n' % (space, row_name, array_delim)
        content += '%sfor (size_t i = 0; i < array.size(); i++)\n' % space
        content += '%s{\n' % space
        content += '%s    %s%s.push_back(to<%s>(array[i]));\n' % (space, prefix, name, elemt_type)
        content += '%s}\n' % space
        return content

    # map赋值
    def gen_field_map_assgin_stmt(self, prefix, typename, name, row_name, map_delims, tabs):
        assert len(map_delims) == 2, map_delims
        delim1 = map_delims[0].strip()
        if delim1 == '\\':
            delim1 = '\\\\'
        delim2 = map_delims[1].strip()
        if delim2 == '\\':
            delim2 = '\\\\'

        k, v = descriptor.map_key_value_types(typename)
        key_type = map_cpp_type(k)
        val_type = map_cpp_type(v)
        space = self.TAB_SPACE * tabs
        content = ''
        content += '%sconst auto& mapitems = Split(%s, "%s");\n' % (space, row_name, delim1)
        content += '%sfor (size_t i = 0; i < mapitems.size(); i++)\n' % space
        content += '%s{\n' % space
        content += '%s    const auto& kv = Split(mapitems[i], "%s");\n' % (space, delim2)
        content += '%s    BEATS_ASSERT(kv.size() == 2);\n' % space
        content += '%s    if(kv.size() == 2)\n' % space
        content += '%s    {\n' % space
        content += '%s        const string& key = to<%s>(kv[0]);\n' % (space, key_type)
        content += '%s        BEATS_ASSERT(%s%s.count(key) == 0);\n' % (space, prefix, name)
        content += '%s        %s%s[key] = to<%s>(kv[1]);\n' % (space, prefix, name, val_type)
        content += '%s    }\n' % space
        content += '%s}\n' % space
        return content

    # 生成字段赋值
    def gen_all_field_assign_stmt(self, struct, prefix, tabs):
        content = ''
        idx = 0
        array_delim = struct['options'].get(predef.OptionArrayDelimeter, predef.DefaultArrayDelimiter)
        map_delims = struct['options'].get(predef.OptionMapDelimeters, predef.DefaultMapDelimiters)

        vec_names, vec_name = self.get_field_range(struct)
        vec_idx = 0
        space = self.TAB_SPACE * tabs
        for field in struct['fields']:
            origin_type = field['original_type_name']
            typename = map_cpp_type(origin_type)

            if typename != 'std::string' and field['name'] in vec_names:
                content += '%s%s%s[%d] = %s;\n' % (space, prefix, vec_name, vec_idx, default_value_by_type(origin_type))

            content += '%sif (!row[%d].empty())\n' % (space, idx)
            content += '%s{\n' % space
            if origin_type.startswith('array'):
                content += self.gen_field_array_assign_stmt(prefix, origin_type, field['name'], ('row[%d]' % idx), array_delim, tabs + 1)
            elif origin_type.startswith('map'):
                content += self.gen_field_map_assgin_stmt(prefix, origin_type, field['name'], ('row[%d]' % idx), map_delims, tabs + 1)
            else:
                if field['name'] in vec_names:
                    content += '%s%s%s[%d] = to<%s>(row[%d]);\n' % (self.TAB_SPACE * (tabs+1), prefix, vec_name, vec_idx, typename, idx)
                    vec_idx += 1
                else:
                    content += '%s%s%s = to<%s>(row[%d]);\n' % (self.TAB_SPACE * (tabs+1), prefix, field['name'], typename, idx)
            content += '%s}\n' % space
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

        if struct['options'][predef.PredefParseKVMode]:
            content += '    static int Load(const char* filepath = nullptr);\n'
            content += '    static int ParseFromRows(const std::vector<std::vector<StringPiece>>& rows, %s* ptr);\n' % struct['name']
            content += '    static const %s* Instance();\n' % struct['name']
            return content

        content += '    static int Load(const char* filepath = nullptr);\n'
        content += '    static int ParseFromRow(const std::vector<StringPiece>& row, %s* ptr);\n' % struct['name']
        content += '    static const std::vector<%s>* GetData(); \n' % struct['name']

        if predef.PredefGetMethodKeys in struct['options']:
            get_keys = self.get_struct_keys(struct, predef.PredefGetMethodKeys, map_cpp_type)
            if len(get_keys) > 0:
                get_args = []
                for tpl in get_keys:
                    typename = tpl[0]
                    if not is_pod_type(typename):
                        typename = 'const %s&' % typename
                    get_args.append(typename + ' ' + tpl[1])

                content += '    static const %s* Get(%s);\n' % (struct['name'], ', '.join(get_args))

        if predef.PredefRangeMethodKeys in struct['options']:
            range_keys = self.get_struct_keys(struct, predef.PredefRangeMethodKeys, map_cpp_type)
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
        if struct['options'][predef.PredefParseKVMode]:
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

    # 生成KV模式的Parse方法
    def gen_kv_parse_method(self, struct):
        rows = struct['data-rows']
        keycol = struct['options'][predef.PredefKeyColumn]
        valcol = struct['options'][predef.PredefValueColumn]
        typcol = int(struct['options'][predef.PredefValueTypeColumn])
        assert keycol > 0 and valcol > 0 and typcol > 0

        keyidx, keyfield = self.get_field_by_column_index(struct, keycol)
        validx, valfield = self.get_field_by_column_index(struct, valcol)
        typeidx, typefield = self.get_field_by_column_index(struct, typcol)

        array_delim = struct['options'].get(predef.OptionArrayDelimeter, predef.DefaultArrayDelimiter)
        map_delims = struct['options'].get(predef.OptionMapDelimeters, predef.DefaultMapDelimiters)

        content = ''
        content += '// parse data object from csv rows\n'
        content += 'int %s::ParseFromRows(const vector<vector<StringPiece>>& rows, %s* ptr)\n' % (struct['name'], struct['name'])
        content += '{\n'
        content += '    BEATS_ASSERT(rows.size() >= %d && rows[0].size() >= %d);\n' % (len(rows), validx)
        content += '    BEATS_ASSERT(ptr != nullptr);\n'
        idx = 0
        for row in rows:
            name = rows[idx][keyidx].strip()
            origin_typename = rows[idx][typeidx].strip()
            typename = map_cpp_type(origin_typename)
            content += '%sif (!rows[%d][%d].empty())\n' % (self.TAB_SPACE, idx, validx)
            content += '%s{\n' % self.TAB_SPACE
            row_name = 'rows[%d][%d]' % (idx, validx)

            if origin_typename.startswith('array'):
                content += self.gen_field_array_assign_stmt('ptr->', origin_typename, name, row_name, array_delim, 2)
            elif origin_typename.startswith('map'):
                content += self.gen_field_map_assgin_stmt('ptr->', origin_typename, name, row_name, map_delims, 2)
            else:
                content += '%sptr->%s = to<%s>(%s);\n' % (self.TAB_SPACE*2, name, typename, row_name)
            content += '%s}\n' % self.TAB_SPACE
            idx += 1
        content += '    return 0;\n'
        content += '}\n'
        return content

    # 生成ParseFromRow方法
    def gen_parse_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct)

        content = ''
        content += '// parse data object from an csv row\n'
        content += 'int %s::ParseFromRow(const vector<StringPiece>& row, %s* ptr)\n' % (struct['name'], struct['name'])
        content += '{\n'
        content += '    BEATS_ASSERT(row.size() >= %d);\n' % len(struct['fields'])
        content += '    BEATS_ASSERT(ptr != nullptr);\n'
        content += self.gen_all_field_assign_stmt(struct, 'ptr->', 1)
        content += '    return 0;\n'
        content += '}\n'
        return content

    # KV模式的Load()方法
    def gen_kv_struct_load_method(self, struct):
        content = ''
        content += '// load data from csv file\n'
        content += 'int %s::Load(const char* filepath /* = nullptr */)\n' % struct['name']
        content += '{\n'
        content += '    if (filepath == nullptr)\n'
        content += '    {\n'
        content += '        filepath = "/csv/%s.csv";\n' % struct['name'].lower()
        content += '    }\n'
        content += '    string content = %s::ReadFileContent(filepath);\n' % util.config_manager_name
        content += '    vector<vector<StringPiece>> rows;\n'
        content += '    auto lines = Split(content, "\\r\\n");\n'
        content += '    BEATS_ASSERT(!lines.empty());\n'
        content += '    for (size_t i = 0; i < lines.size(); i++)\n'
        content += '    {\n'
        content += '        if (!lines[i].empty())\n'
        content += '        {\n'
        content += '            const auto& row = Split(lines[i], ",");\n'
        content += '            if (!row.empty())\n'
        content += '            {\n'
        content += '                rows.push_back(row);\n'
        content += '            }\n'
        content += '        }\n'
        content += '    }\n'
        content += '    %s* dataptr = new %s();\n' % (struct['name'], struct['name'])
        content += '    %s::ParseFromRows(rows, dataptr);\n' % struct['name']
        varname = self.get_instance_data_name(struct['name'])
        content += '    delete %s;\n' % varname
        content += '    %s = dataptr;\n' % varname
        content += '    return 0;\n'
        content += '}\n\n'
        return content

    # 生成Load()方法
    def gen_struct_load_method(self, struct):
        content = ''
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_struct_load_method(struct)

        varname = self.get_instance_data_name(struct['name'])
        content += '// load data from csv file\n'
        content += 'int %s::Load(const char* filepath /* = nullptr */)\n' % struct['name']
        content += '{\n'
        content += '    if (filepath == nullptr)\n'
        content += '    {\n'
        content += '        filepath = "/csv/%s.csv";\n' % struct['name'].lower()
        content += '    }\n'
        content += '    vector<%s>* dataptr = new vector<%s>;\n' % (struct['name'], struct['name'])
        content += '    string content = %s::ReadFileContent(filepath);\n' % util.config_manager_name
        content += '    auto lines = Split(content, "\\r\\n");\n'
        content += '    BEATS_ASSERT(!lines.empty());\n'
        content += '    for (size_t i = 0; i < lines.size(); i++)\n'
        content += '    {\n'
        content += '        if (!lines[i].empty())\n'
        content += '        {\n'
        content += '            const auto& row = Split(lines[i], ",");\n'
        content += '            if (!row.empty())\n'
        content += '            {\n'
        content += '                %s item;\n' % struct['name']
        content += '                %s::ParseFromRow(row, &item);\n' % struct['name']
        content += '                dataptr->push_back(item);\n'
        content += '            }\n'
        content += '        }\n'
        content += '    }\n'
        content += '    delete %s;\n' % varname
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

    # 生成Get()方法
    def gen_struct_get_method(self, struct):
        content = ''
        if struct['options'][predef.PredefParseKVMode]:
            return content

        keys = self.get_struct_keys(struct, predef.PredefGetMethodKeys, map_cpp_type)
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

        keys = self.get_struct_keys(struct, predef.PredefRangeMethodKeys, map_cpp_type)
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

    # 生成全局Load和Clear方法
    def gen_manager_static_method(self, descriptors):
        content = ''
        content += 'void %s::LoadAll()\n' % util.config_manager_name
        content += '{\n'
        for struct in descriptors:
            content += '    %s::Load();\n' % struct['name']
        content += '}\n\n'

        content += 'void %s::ClearAll()\n' % util.config_manager_name
        content += '{\n'
        for struct in descriptors:
            content += '    delete %s;\n' % self.get_instance_data_name(struct['name'])
            content += '    %s = nullptr;\n' % self.get_instance_data_name(struct['name'])
        content += '}\n\n'

        content += '//Load content of an asset file\n'
        content += 'std::string %s::ReadFileContent(const std::string& filepath)\n' % util.config_manager_name
        content += '{\n'
        content += '    const string& path = CResourceManager::GetInstance()->GetResourcePath(eRT_Resource) + filepath;\n'
        content += '    CSerializer serializer(path.c_str());\n'
        content += '    return string((const char*)serializer.GetBuffer(), serializer.GetWritePos());\n'
        content += '}\n\n\n'

        return content

    # 生成头文件声明
    def gen_cpp_header(self, struct):
        content = ''
        content += self.gen_cpp_struct_define(struct)
        content += '\n'
        content += self.gen_struct_method_declare(struct)
        content += '};\n\n'
        return content

    # 生成源文件定义
    def gen_cpp_source(self, struct):
        content = ''
        content += self.gen_struct_data_method(struct)
        content += self.gen_struct_get_method(struct)
        content += self.gen_struct_range_method(struct)
        content += self.gen_struct_load_method(struct)
        content += self.gen_parse_method(struct)
        return content

    #
    def run(self, descriptors, args):
        params = util.parse_args(args)
        h_include_headers = [
            '#include <stdint.h>',
            '#include <string>',
            '#include <vector>',
            '#include "Utility/Range.h"',
        ]
        header_content = '// This file is auto-generated by taxi v%s, DO NOT EDIT!\n\n#pragma once\n\n' % util.version_string
        header_content += '\n'.join(h_include_headers) + '\n\n'
        header_content += 'class %s\n' % util.config_manager_name
        header_content += '{\n'
        header_content += 'public:\n'
        header_content += '    // Load all configurations\n'
        header_content += '    static void LoadAll();\n\n'
        header_content += '    // Clear all configurations\n'
        header_content += '    static void ClearAll();\n\n'
        header_content += '    //Load content of an asset file\n'
        header_content += '    static std::string ReadFileContent(const std::string& filepath);\n'
        header_content += '};\n\n'

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

        if 'pkg' in params:
            header_content += '\nnamespace %s\n{\n\n' % params['pkg']
            cpp_content += '\nnamespace %s\n{\n\n' % params['pkg']

        class_content = ''
        for struct in descriptors:
            print('start generate', struct['source'])
            self.setup_comment(struct)
            self.setup_key_value_mode(struct)

            if not data_only:
                header_content += self.gen_cpp_header(struct)
                class_content += self.gen_cpp_source(struct)

        if not data_only:
            static_define_content = 'namespace \n{\n'
            for struct in descriptors:
                static_define_content += self.gen_global_static_define(struct)
            static_define_content += '}\n\n'

            if 'pkg' in params:
                header_content += '\n} // namespace %s \n' % params['pkg']  # namespace
            outputfile = params.get(predef.OptionOutSourceFile, 'AutogenConfig')
            filename = outputfile + '.h'
            filename = os.path.abspath(filename)
            util.compare_and_save_content(filename, header_content, 'gbk')
            print('wrote header file to', filename)

            cpp_content += static_define_content
            cpp_content += self.gen_manager_static_method(descriptors)
            cpp_content += class_content
            if 'pkg' in params:
                cpp_content += '\n} // namespace %s \n' % params['pkg']  # namespace
            filename = outputfile + '.cpp'
            filename = os.path.abspath(filename)
            util.compare_and_save_content(filename, cpp_content, 'gbk')
            print('wrote source file to', filename)

        if not no_data or data_only:
            for struct in descriptors:
                self.write_data_rows(struct, params)


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


# 默认值
def default_value_by_type(typename):
    if typename == 'bool':
        return 'false'
    elif descriptor.is_integer_type(typename):
        return '0'
    elif descriptor.is_floating_type(typename):
        return '0.0'
    return ''


# POD类型
def is_pod_type(typ):
    assert len(typ.strip()) > 0
    return not typ.startswith('std::')  # std::string, std::vector, std::map
