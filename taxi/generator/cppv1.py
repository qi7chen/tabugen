# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import unittest
import taxi.descriptor.types as types
import taxi.descriptor.predef as predef
import taxi.descriptor.lang as lang
import taxi.descriptor.strutil as strutil
import taxi.generator.genutil as genutil
import taxi.version as version


CPP_METHOD_TEMPLATE = """
    // Load all configurations
    static void LoadAll();

    // Clear all configurations
    static void ClearAll();

    // Read content from an asset file
    static std::string ReadFileContent(const char* filepath);
    
    // default loader
    static std::function<std::string(const char*)> reader;
"""

CPP_PARSE_FUN_TEMPLATE = """
// parse value from text
template <typename T>
inline T ParseValue(StringPiece text)
{
    text = trimWhitespace(text);
    if (text.empty())
    {
        return T();
    }
    return to<T>(text);
}

"""


# C++ code generator
class CppV1Generator:
    TAB_SPACE = '    '

    def __init__(self):
        pass

    @staticmethod
    def name():
        return "cpp-v1"

    def get_instance_data_name(self, name):
        return '_instance_%s' % name.lower()

    def gen_equal_stmt(self, prefix, struct, key):
        keys = genutil.get_struct_keys(struct, key, lang.map_cpp_type)
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

        space = self.TAB_SPACE * (tabs + 1)
        elemt_type = lang.map_cpp_type(types.array_element_type(typename))
        content = '%s{\n' % (self.TAB_SPACE * tabs)
        content += '%sconst auto& array = Split(%s, "%s", true);\n' % (space, row_name, array_delim)
        content += '%sfor (size_t i = 0; i < array.size(); i++)\n' % space
        content += '%s{\n' % space
        content += '%s    %s%s.push_back(ParseValue<%s>(array[i]));\n' % (space, prefix, name, elemt_type)
        content += '%s}\n' % space
        content += '%s}\n' % (self.TAB_SPACE * tabs)
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

        k, v = types.map_key_value_types(typename)
        key_type = lang.map_cpp_type(k)
        val_type = lang.map_cpp_type(v)
        space = self.TAB_SPACE * (tabs + 1)
        content = '%s{\n' % (self.TAB_SPACE * tabs)
        content += '%sconst auto& mapitems = Split(%s, "%s", true);\n' % (space, row_name, delim1)
        content += '%sfor (size_t i = 0; i < mapitems.size(); i++)\n' % space
        content += '%s{\n' % space
        content += '%s    const auto& kv = Split(mapitems[i], "%s", true);\n' % (space, delim2)
        content += '%s    ASSERT(kv.size() == 2);\n' % space
        content += '%s    if(kv.size() == 2)\n' % space
        content += '%s    {\n' % space
        content += '%s        const auto& key = ParseValue<%s>(kv[0]);\n' % (space, key_type)
        content += '%s        ASSERT(%s%s.count(key) == 0);\n' % (space, prefix, name)
        content += '%s        %s%s[key] = ParseValue<%s>(kv[1]);\n' % (space, prefix, name, val_type)
        content += '%s    }\n' % space
        content += '%s}\n' % space
        content += '%s}\n' % (self.TAB_SPACE * tabs)
        return content

    # 内部class赋值
    def gen_inner_class_field_assgin_stmt(self, struct, prefix, inner_fields):
        content = ''
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerTypeName]
        start, end, step = genutil.get_inner_class_range(struct)
        assert start > 0 and end > 0 and step > 1
        content += '    for (int i = %s; i < %s; i += %s) \n' % (start, end, step)
        content += '    {\n'
        content += '        %s item;\n' % inner_class_type
        for n in range(step):
            field = inner_fields[n]
            origin_type = field['original_type_name']
            typename = lang.map_cpp_type(origin_type)
            content += '        item.%s = ParseValue<%s>(row[i + %d]);\n' % (field['name'], typename, n)
        content += '        %s%s.push_back(item);\n' % (prefix, inner_var_name)
        content += '    }\n'
        return content

    # 生成字段赋值
    def gen_all_field_assign_stmt(self, struct, prefix, tabs):
        content = ''
        idx = 0
        array_delim = struct['options'].get(predef.OptionArrayDelimeter, predef.DefaultArrayDelimiter)
        map_delims = struct['options'].get(predef.OptionMapDelimeters, predef.DefaultMapDelimiters)

        inner_class_done = False
        inner_field_names, inner_fields = genutil.get_inner_class_fields(struct)

        vec_names, vec_name = genutil.get_vec_field_range(struct)
        vec_idx = 0
        space = self.TAB_SPACE * tabs
        for field in struct['fields']:
            field_name = field['name']
            if field_name in inner_field_names:
                if not inner_class_done:
                    inner_class_done = True
                    content += self.gen_inner_class_field_assgin_stmt(struct, prefix, inner_fields)
            else:
                origin_type = field['original_type_name']
                typename = lang.map_cpp_type(origin_type)

                if typename != 'std::string' and field['name'] in vec_names:
                    content += '%s%s%s[%d] = %s;\n' % (space, prefix, vec_name, vec_idx, lang.default_value_by_cpp_type(origin_type))

                if origin_type.startswith('array'):
                    content += self.gen_field_array_assign_stmt(prefix, origin_type, field_name, ('row[%d]' % idx), array_delim, tabs)
                elif origin_type.startswith('map'):
                    content += self.gen_field_map_assgin_stmt(prefix, origin_type, field_name, ('row[%d]' % idx), map_delims, tabs)
                else:
                    if field['name'] in vec_names:
                        content += '%s%s%s[%d] = ParseValue<%s>(row[%d]);\n' % (self.TAB_SPACE * (tabs), prefix, vec_name, vec_idx, typename, idx)
                        vec_idx += 1
                    else:
                        content += '%s%s%s = ParseValue<%s>(row[%d]);\n' % (self.TAB_SPACE * (tabs), prefix, field_name, typename, idx)
            idx += 1
        return content

    # 生成class定义结构
    def gen_cpp_struct_define(self, struct):
        content = '// %s\n' % struct['comment']
        content += 'struct %s \n{\n' % struct['name']
        fields = struct['fields']
        if struct['options'][predef.PredefParseKVMode]:
            fields = genutil.get_struct_kv_fields(struct)

        inner_class_done = False
        inner_typename = ''
        inner_var_name = ''
        inner_field_names, inner_fields = genutil.get_inner_class_fields(struct)
        if len(inner_fields) > 0:
            content += self.gen_inner_struct_define(struct, inner_fields)
            inner_type_class = struct["options"][predef.PredefInnerTypeClass]
            inner_var_name = struct["options"][predef.PredefInnerTypeName]
            inner_typename = 'std::vector<%s>' % inner_type_class

        vec_done = False
        vec_names, vec_name = genutil.get_vec_field_range(struct)

        max_name_len = strutil.max_field_length(fields, 'name', None)
        max_type_len = strutil.max_field_length(fields, 'original_type_name', lang.map_cpp_type)
        if len(inner_typename) > max_type_len:
            max_type_len = len(inner_typename)

        for field in fields:
            field_name = field['name']
            if field_name in inner_field_names:
                if not inner_class_done:
                    typename = strutil.pad_spaces(inner_typename, max_type_len + 1)
                    name = strutil.pad_spaces(inner_var_name, max_name_len + 8)
                    content += '    %s %s; //\n' % (typename, name)
                    inner_class_done = True

            else:
                typename = lang.map_cpp_type(field['original_type_name'])
                assert typename != "", field['original_type_name']
                typename = strutil.pad_spaces(typename, max_type_len + 1)
                if field_name not in vec_names:
                    name = lang.name_with_default_cpp_value(field, typename)
                    name = strutil.pad_spaces(name, max_name_len + 8)
                    content += '    %s %s // %s\n' % (typename, name, field['comment'])
                elif not vec_done:
                    name = '%s[%d];' % (vec_name, len(vec_names))
                    name = strutil.pad_spaces(name, max_name_len + 8)
                    content += '    %s %s // %s\n' % (typename, name, field['comment'])
                    vec_done = True

        return content

    # 内部class定义
    def gen_inner_struct_define(self, struct, inner_fields):
        content = ''
        class_name = struct["options"][predef.PredefInnerTypeClass]
        content += '    struct %s \n' % class_name
        content += '    {\n'
        max_name_len = strutil.max_field_length(inner_fields, 'name', None)
        max_type_len = strutil.max_field_length(inner_fields, 'original_type_name', lang.map_cpp_type)
        for field in inner_fields:
            typename = lang.map_cpp_type(field['original_type_name'])
            assert typename != "", field['original_type_name']
            typename = strutil.pad_spaces(typename, max_type_len + 1)
            name = lang.name_with_default_cpp_value(field, typename)
            name = strutil.pad_spaces(name, max_name_len + 8)
            content += '        %s %s // %s\n' % (typename, name, field['comment'])
        content += '    };\n\n'

        return content

    # class静态函数声明
    def gen_struct_method_declare(self, struct):
        content = ''

        if struct['options'][predef.PredefParseKVMode]:
            content += '    static int Load(const char* filepath);\n'
            content += '    static int ParseFromRows(const std::vector<std::vector<StringPiece>>& rows, %s* ptr);\n' % struct['name']
            content += '    static const %s* Instance();\n' % struct['name']
            return content

        content += '    static int Load(const char* filepath);\n'
        content += '    static int ParseFromRow(const std::vector<StringPiece>& row, %s* ptr);\n' % struct['name']
        content += '    static const std::vector<%s>* GetData(); \n' % struct['name']

        if predef.PredefGetMethodKeys in struct['options']:
            get_keys = genutil.get_struct_keys(struct, predef.PredefGetMethodKeys, lang.map_cpp_type)
            if len(get_keys) > 0:
                get_args = []
                for tpl in get_keys:
                    typename = tpl[0]
                    if not lang.is_cpp_pod_type(typename):
                        typename = 'const %s&' % typename
                    get_args.append(typename + ' ' + tpl[1])

                content += '    static const %s* Get(%s);\n' % (struct['name'], ', '.join(get_args))

        if predef.PredefRangeMethodKeys in struct['options']:
            range_keys = genutil.get_struct_keys(struct, predef.PredefRangeMethodKeys, lang.map_cpp_type)
            range_args = []
            for tpl in range_keys:
                typename = tpl[0]
                if not lang.is_cpp_pod_type(typename):
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
            content += '    ASSERT(%s != nullptr);\n' % varname
            content += '    return %s;\n' % varname
            content += '}\n\n'
        else:
            content += 'const std::vector<%s>* %s::GetData()\n' % (struct['name'], struct['name'])
            content += '{\n'
            content += '    ASSERT(%s != nullptr);\n' % varname
            content += '    return %s;\n' % varname
            content += '}\n\n'
        return content

    # 生成KV模式的Parse方法
    def gen_kv_parse_method(self, struct):
        rows = struct['data_rows']
        keycol = struct['options'][predef.PredefKeyColumn]
        valcol = struct['options'][predef.PredefValueColumn]
        typcol = int(struct['options'][predef.PredefValueTypeColumn])
        assert keycol > 0 and valcol > 0 and typcol > 0

        keyidx, keyfield = genutil.get_field_by_column_index(struct, keycol)
        validx, valfield = genutil.get_field_by_column_index(struct, valcol)
        typeidx, typefield = genutil.get_field_by_column_index(struct, typcol)

        array_delim = struct['options'].get(predef.OptionArrayDelimeter, predef.DefaultArrayDelimiter)
        map_delims = struct['options'].get(predef.OptionMapDelimeters, predef.DefaultMapDelimiters)

        content = ''
        content += '// parse data object from csv rows\n'
        content += 'int %s::ParseFromRows(const vector<vector<StringPiece>>& rows, %s* ptr)\n' % (struct['name'], struct['name'])
        content += '{\n'
        content += '    ASSERT(rows.size() >= %d && rows[0].size() >= %d);\n' % (len(rows), validx)
        content += '    ASSERT(ptr != nullptr);\n'
        idx = 0
        for row in rows:
            name = rows[idx][keyidx].strip()
            origin_typename = rows[idx][typeidx].strip()
            typename = lang.map_cpp_type(origin_typename)
            row_name = 'rows[%d][%d]' % (idx, validx)
            if origin_typename.startswith('array'):
                content += self.gen_field_array_assign_stmt('ptr->', origin_typename, name, row_name, array_delim, 1)
            elif origin_typename.startswith('map'):
                content += self.gen_field_map_assgin_stmt('ptr->', origin_typename, name, row_name, map_delims, 1)
            else:
                content += '%sptr->%s = ParseValue<%s>(%s);\n' % (self.TAB_SPACE, name, typename, row_name)
            idx += 1
        content += '    return 0;\n'
        content += '}\n\n'
        return content

    # 生成ParseFromRow方法
    def gen_parse_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct)

        content = ''
        content += '// parse data object from an csv row\n'
        content += 'int %s::ParseFromRow(const vector<StringPiece>& row, %s* ptr)\n' % (struct['name'], struct['name'])
        content += '{\n'
        content += '    ASSERT(row.size() >= %d);\n' % len(struct['fields'])
        content += '    ASSERT(ptr != nullptr);\n'
        content += self.gen_all_field_assign_stmt(struct, 'ptr->', 1)
        content += '    return 0;\n'
        content += '}\n\n'
        return content

    # KV模式的Load()方法
    def gen_kv_struct_load_method(self, struct):
        content = ''
        content += '// load data from csv file\n'
        content += 'int %s::Load(const char* filepath)\n' % struct['name']
        content += '{\n'
        content += '    string content = %s::reader(filepath);\n' % strutil.config_manager_name
        content += '    MutableStringPiece sp((char*)content.data(), content.size());\n'
        content += '    sp.replaceAll("\\r\\n", " \\n");\n'
        content += '    vector<vector<StringPiece>> rows;\n'
        content += '    auto lines = Split(sp, "\\n");\n'
        content += '    ASSERT(!lines.empty());\n'
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
        content += 'int %s::Load(const char* filepath)\n' % struct['name']
        content += '{\n'
        content += '    vector<%s>* dataptr = new vector<%s>;\n' % (struct['name'], struct['name'])
        content += '    string content = %s::reader(filepath);\n' % strutil.config_manager_name
        content += '    MutableStringPiece sp((char*)content.data(), content.size());\n'
        content += '    sp.replaceAll("\\r\\n", " \\n");\n'
        content += '    auto lines = Split(sp, "\\n");\n'
        content += '    ASSERT(!lines.empty());\n'
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

        keys = genutil.get_struct_keys(struct, predef.PredefGetMethodKeys, lang.map_cpp_type)
        if len(keys) == 0:
            return content

        formal_param = []
        arg_names = []
        for tpl in keys:
            typename = tpl[0]
            if not lang.is_cpp_pod_type(typename):
                typename = 'const %s&' % typename
            formal_param.append('%s %s' % (typename, tpl[1]))
            arg_names.append(tpl[1])

        content += 'const %s* %s::Get(%s)\n' % (struct['name'], struct['name'], ', '.join(formal_param))
        content += '{\n'
        content += '    const vector<%s>* dataptr = GetData();\n' % struct['name']
        content += '    ASSERT(dataptr != nullptr && dataptr->size() > 0);\n'
        content += '    for (size_t i = 0; i < dataptr->size(); i++)\n'
        content += '    {\n'
        content += '        if (%s)\n' % self.gen_equal_stmt('dataptr->at(i).', struct, 'get-keys')
        content += '        {\n'
        content += '            return &dataptr->at(i);\n'
        content += '        }\n'
        content += '    }\n'
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

        keys = genutil.get_struct_keys(struct, predef.PredefRangeMethodKeys, lang.map_cpp_type)
        assert len(keys) > 0

        formal_param = []
        params = []
        arg_names = []
        for tpl in keys:
            typename = tpl[0]
            if not lang.is_cpp_pod_type(typename):
                typename = 'const %s&' % typename
            formal_param.append('%s %s' % (typename, tpl[1]))
            arg_names.append(tpl[1])

        content += 'std::vector<const %s*> %s::GetRange(%s)\n' % (
            struct['name'], struct['name'], ', '.join(formal_param))
        content += '{\n'
        content += '    const vector<%s>* dataptr = GetData();\n' % struct['name']
        content += '    std::vector<const %s*> range;\n' % struct['name']
        content += '    ASSERT(dataptr != nullptr && dataptr->size() > 0);\n'
        content += '    for (size_t i = 0; i < dataptr->size(); i++)\n'
        content += '    {\n'
        content += '        if (%s)\n' % self.gen_equal_stmt('dataptr->at(i).', struct, 'range-keys')
        content += '        {\n'
        content += '            range.push_back(&dataptr->at(i));\n'
        content += '        }\n'
        content += '    }\n'
        content += '    return range;\n'
        content += '}\n\n'
        return content

    # 生成全局Load和Clear方法
    def gen_manager_static_method(self, descriptors):
        content = ''
        content += 'void %s::LoadAll()\n' % strutil.config_manager_name
        content += '{\n'
        content += '    ASSERT(reader);\n'
        for struct in descriptors:
            content += '    %s::Load("%s.csv");\n' % (struct['name'], struct['name'].lower())
        content += '}\n\n'

        content += 'void %s::ClearAll()\n' % strutil.config_manager_name
        content += '{\n'
        for struct in descriptors:
            content += '    delete %s;\n' % self.get_instance_data_name(struct['name'])
            content += '    %s = nullptr;\n' % self.get_instance_data_name(struct['name'])
        content += '}\n\n'

        content += '//Load content of an asset file\n'
        content += 'std::string %s::ReadFileContent(const char* filepath)\n' % strutil.config_manager_name
        content += '{\n'
        content += '    ASSERT(filepath != nullptr);\n'
        content += '    std::ifstream ifs(filepath);\n'
        content += '    ASSERT(!ifs.fail());\n'
        content += '    std::string content;\n'
        content += '    content.assign(std::istreambuf_iterator<char>(ifs), std::istreambuf_iterator<char>());\n'
        content += '    return std::move(content);\n'
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
    def run(self, descriptors, params):
        headerfile = params.get(predef.OptionOutSourceFile, 'AutogenConfig') + '.h'
        sourcefile = params.get(predef.OptionOutSourceFile, 'AutogenConfig') + '.cpp'

        h_include_headers = [
            '#include <stdint.h>',
            '#include <string>',
            '#include <vector>',
            '#include <functional>',
            '#include "Utility/Range.h"',
        ]
        header_content = '// This file is auto-generated by taxi v%s, DO NOT EDIT!\n\n#pragma once\n\n' % version.VER_STRING
        header_content += '\n'.join(h_include_headers) + '\n\n'

        cpp_include_headers = [
            '#include "%s"' % os.path.basename(headerfile),
            '#include <stddef.h>',
            '#include <assert.h>',
            '#include <memory>',
            '#include <fstream>',
            '#include "Utility/Conv.h"',
            '#include "Utility/StringUtil.h"',
        ]
        cpp_content = '// This file is auto-generated by taxi v%s, DO NOT EDIT!\n\n' % version.VER_STRING
        if predef.OptionPchFile in params:
            pchfile = '#include "%s"' % params[predef.OptionPchFile]
            cpp_include_headers = [pchfile] + cpp_include_headers

        cpp_content += '\n'.join(cpp_include_headers) + '\n\n'
        cpp_content += 'using namespace std;\n\n'
        cpp_content += '#ifndef ASSERT\n'
        cpp_content += '#define ASSERT assert\n'
        cpp_content += '#endif\n\n'
        cpp_content += CPP_PARSE_FUN_TEMPLATE

        if 'pkg' in params:
            header_content += '\nnamespace %s\n{\n\n' % params['pkg']
            cpp_content += '\nnamespace %s\n{\n\n' % params['pkg']

        cpp_content += 'std::function<std::string(const char*)> %s::reader = %s::ReadFileContent;\n\n' % (
            strutil.config_manager_name, strutil.config_manager_name)

        header_content += 'class %s\n' % strutil.config_manager_name
        header_content += '{\n'
        header_content += 'public:\n'
        header_content += CPP_METHOD_TEMPLATE
        header_content += '};\n\n'

        data_only = params.get(predef.OptionDataOnly, False)
        no_data = params.get(predef.OptionNoData, False)

        class_content = ''
        for struct in descriptors:
            print(strutil.current_time(), 'start generate', struct['source'])
            genutil.setup_comment(struct)
            genutil.setup_key_value_mode(struct)

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

            encoding = params.get(predef.OptionSourceEncoding, 'utf-8')
            filename = os.path.abspath(headerfile)
            strutil.compare_and_save_content(filename, header_content, encoding)
            print('wrote header file to', filename)

            cpp_content += static_define_content
            cpp_content += self.gen_manager_static_method(descriptors)
            cpp_content += class_content
            if 'pkg' in params:
                cpp_content += '\n} // namespace %s \n' % params['pkg']  # namespace

            filename = os.path.abspath(sourcefile)
            strutil.compare_and_save_content(filename, cpp_content, encoding)
            print('wrote source file to', filename)


