# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import taksi.typedef as types
import taksi.predef as predef
import taksi.lang as lang
import taksi.strutil as strutil
import taksi.generator.genutil as genutil
import taksi.generator.cpp.template as cpp_template
import taksi.version as version


# 生成C++加载CSV文件数据代码
class CppCsvLoadGenerator:
    TAB_SPACE = '    '

    def __init__(self):
        self.array_delim = ','
        self.map_delims = [',', '=']

    # 初始化array, map分隔符
    def setup(self, array_delim, map_delims):
        self.array_delim = array_delim
        self.map_delims = map_delims

    #
    def get_instance_data_name(self, name):
        return '_instance_%s' % name.lower()

    # 生成赋值表达式
    def gen_equal_stmt(self, prefix, struct, key):
        keys = genutil.get_struct_keys(struct, key, lang.map_cpp_type)
        args = []
        for tpl in keys:
            args.append('%s%s == %s' % (prefix, tpl[1], tpl[1]))
        return ' && '.join(args)

    # array赋值
    def gen_field_array_assign_stmt(self, prefix, typename, name, row_name, tabs):
        assert isinstance(self.array_delim, str) and len(self.array_delim) == 1
        space = self.TAB_SPACE * (tabs + 1)
        elemt_type = lang.map_cpp_type(types.array_element_type(typename))
        content = '%s{\n' % (self.TAB_SPACE * tabs)
        content += '%sconst auto& array = Split(%s, "%s", true);\n' % (space, row_name, self.array_delim)
        content += '%sfor (size_t i = 0; i < array.size(); i++)\n' % space
        content += '%s{\n' % space
        content += '%s    %s%s.push_back(ParseValue<%s>(array[i]));\n' % (space, prefix, name, elemt_type)
        content += '%s}\n' % space
        content += '%s}\n' % (self.TAB_SPACE * tabs)
        return content

    # map赋值
    def gen_field_map_assgin_stmt(self, prefix, typename, name, row_name, tabs):
        assert len(self.map_delims) == 2
        delim1 = self.map_delims[0]
        delim2 = self.map_delims[1]

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
    def gen_inner_class_field_assgin_stmt(self, struct, prefix):
        content = ''
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerTypeName]
        inner_fields = genutil.get_inner_class_struct_fields(struct)
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

        inner_class_done = False
        inner_field_names, inner_fields = genutil.get_inner_class_mapped_fields(struct)

        vec_names, vec_name = genutil.get_vec_field_range(struct)
        vec_idx = 0
        space = self.TAB_SPACE * tabs
        for field in struct['fields']:
            field_name = field['name']
            if field_name in inner_field_names:
                if not inner_class_done:
                    inner_class_done = True
                    content += self.gen_inner_class_field_assgin_stmt(struct, prefix)
            else:
                origin_type = field['original_type_name']
                typename = lang.map_cpp_type(origin_type)

                if typename != 'std::string' and field['name'] in vec_names:
                    content += '%s%s%s[%d] = %s;\n' % (
                    space, prefix, vec_name, vec_idx, lang.default_value_by_cpp_type(origin_type))

                if origin_type.startswith('array'):
                    content += self.gen_field_array_assign_stmt(prefix, origin_type, field_name,
                                                                ('row[%d]' % idx), tabs)
                elif origin_type.startswith('map'):
                    content += self.gen_field_map_assgin_stmt(prefix, origin_type, field_name,
                                                              ('row[%d]' % idx), tabs)
                else:
                    if field['name'] in vec_names:
                        content += '%s%s%s[%d] = ParseValue<%s>(row[%d]);\n' % (
                        self.TAB_SPACE * (tabs), prefix, vec_name, vec_idx, typename, idx)
                        vec_idx += 1
                    else:
                        content += '%s%s%s = ParseValue<%s>(row[%d]);\n' % (
                        self.TAB_SPACE * (tabs), prefix, field_name, typename, idx)
            idx += 1
        return content

    # class静态函数声明
    def gen_struct_method_declare(self, struct):
        content = ''

        if struct['options'][predef.PredefParseKVMode]:
            content += '    static int Load(const char* filepath);\n'
            content += '    static int ParseFromRows(const std::vector<std::vector<StringPiece>>& rows, %s* ptr);\n' % \
                       struct['name']
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

        content = ''
        content += '// parse data object from csv rows\n'
        content += 'int %s::ParseFromRows(const vector<vector<StringPiece>>& rows, %s* ptr)\n' % (
        struct['name'], struct['name'])
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
                content += self.gen_field_array_assign_stmt('ptr->', origin_typename, name, row_name, 1)
            elif origin_typename.startswith('map'):
                content += self.gen_field_map_assgin_stmt('ptr->', origin_typename, name, row_name, 1)
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
        content += '        auto line = trimWhitespace(lines[i]);\n'
        content += '        if (!line.empty())\n'
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
        content += '        auto line = trimWhitespace(lines[i]);\n'
        content += '        if (!line.empty())\n'
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
            filename = strutil.camel_to_snake(struct['camel_case_name'])
            content += '    %s::Load("%s.csv");\n' % (struct['name'], filename)
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

    # 生成源文件定义
    def gen_cpp_source(self, struct):
        content = ''
        content += self.gen_struct_data_method(struct)
        content += self.gen_struct_get_method(struct)
        content += self.gen_struct_range_method(struct)
        content += self.gen_struct_load_method(struct)
        content += self.gen_parse_method(struct)
        return content

    def gen_global_class(self):
        content = ''
        content += 'class %s\n' % strutil.config_manager_name
        content += '{\n'
        content += 'public:\n'
        content += cpp_template.CPP_MANAGER_METHOD_TEMPLATE
        content += '};\n\n'
        return content

    def gen_source_method(self, descriptors, args, headerfile):
        cpp_include_headers = [
            '#include "%s"' % os.path.basename(headerfile),
            '#include <stddef.h>',
            '#include <assert.h>',
            '#include <memory>',
            '#include <fstream>',
            '#include "Utility/Conv.h"',
            '#include "Utility/StringUtil.h"',
        ]
        cpp_content = '// This file is auto-generated by TAKSi v%s, DO NOT EDIT!\n\n' % version.VER_STRING
        if args.cpp_pch is not None:
            pchfile = '#include "%s"' % args.cpp_pch
            cpp_include_headers = [pchfile] + cpp_include_headers

        cpp_content += '\n'.join(cpp_include_headers) + '\n\n'
        cpp_content += 'using namespace std;\n\n'
        cpp_content += '#ifndef ASSERT\n'
        cpp_content += '#define ASSERT assert\n'
        cpp_content += '#endif\n\n'
        cpp_content += cpp_template.CPP_PARSE_FUN_TEMPLATE

        if args.package is not None:
            cpp_content += '\nnamespace %s\n{\n\n' % args.package

        cpp_content += 'std::function<std::string(const char*)> %s::reader = %s::ReadFileContent;\n\n' % (
            strutil.config_manager_name, strutil.config_manager_name)

        static_var_content = 'namespace \n{\n'
        for struct in descriptors:
            static_var_content += self.gen_global_static_define(struct)
        static_var_content += '}\n\n'

        class_content = ''
        for struct in descriptors:
            class_content += self.gen_cpp_source(struct)

        cpp_content += static_var_content
        cpp_content += self.gen_manager_static_method(descriptors)
        cpp_content += class_content
        if args.package is not None:
            cpp_content += '\n} // namespace %s \n' % args.package  # namespace
        return cpp_content

