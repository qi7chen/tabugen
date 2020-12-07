# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import tabular.typedef as types
import tabular.predef as predef
import tabular.lang as lang
import tabular.version as version
import tabular.util.strutil as strutil
import tabular.util.structutil as structutil
import tabular.generator.cpp.template as cpp_template


# 生成C++加载CSV文件数据代码
class CppCsvLoadGenerator:
    TAB_SPACE = '    '

    def __init__(self, gen_dataload):
        self.array_delim = ','
        self.map_delims = [',', '=']
        self.out_csv_delim = ','
        self.config_manager_name = ''
        self.gen_dataload = gen_dataload

    # 初始化array, map分隔符
    def setup(self, array_delim, map_delims, out_csv_delim, name):
        self.array_delim = array_delim
        self.map_delims = map_delims
        self.out_csv_delim = out_csv_delim
        self.config_manager_name = name

    #
    def get_instance_data_name(self, name):
        return '_instance_%s' % name.lower()

    # 生成赋值表达式
    def gen_equal_stmt(self, prefix, struct, key):
        keys = structutil.get_struct_keys(struct, key, lang.map_cpp_type)
        assert len(keys) > 0
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
        content += '%sconst auto& array = Split(%s, TAB_ARRAY_DELIM, true);\n' % (space, row_name)
        content += '%sfor (size_t i = 0; i < array.size(); i++)\n' % space
        content += '%s{\n' % space
        content += '%s    %s%s.push_back(ParseTextAs<%s>(array[i]));\n' % (space, prefix, name, elemt_type)
        content += '%s}\n' % space
        content += '%s}\n' % (self.TAB_SPACE * tabs)
        return content

    # map赋值
    def gen_field_map_assgin_stmt(self, prefix, typename, name, row_name, tabs):
        assert len(self.map_delims) == 2

        k, v = types.map_key_value_types(typename)
        key_type = lang.map_cpp_type(k)
        val_type = lang.map_cpp_type(v)
        space = self.TAB_SPACE * (tabs + 1)
        content = '%s{\n' % (self.TAB_SPACE * tabs)
        content += '%sconst auto& dict = Split(%s, TAB_MAP_DELIM1, true);\n' % (space, row_name)
        content += '%sfor (size_t i = 0; i < dict.size(); i++)\n' % space
        content += '%s{\n' % space
        content += '%s    const auto& kv = Split(dict[i], TAB_MAP_DELIM2, true);\n' % space
        content += '%s    ASSERT(kv.size() == 2);\n' % space
        content += '%s    if(kv.size() == 2)\n' % space
        content += '%s    {\n' % space
        content += '%s        const auto& key = ParseTextAs<%s>(kv[0]);\n' % (space, key_type)
        content += '%s        ASSERT(%s%s.count(key) == 0);\n' % (space, prefix, name)
        content += '%s        %s%s[key] = ParseTextAs<%s>(kv[1]);\n' % (space, prefix, name, val_type)
        content += '%s    }\n' % space
        content += '%s}\n' % space
        content += '%s}\n' % (self.TAB_SPACE * tabs)
        return content

    # 内部class赋值
    def gen_inner_class_field_assgin_stmt(self, struct, prefix):
        content = ''
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerTypeName]
        inner_fields = structutil.get_inner_class_struct_fields(struct)
        start, end, step = structutil.get_inner_class_range(struct)
        assert start > 0 and end > 0 and step > 1
        content += '    for (int i = %s; i < %s; i += %s) \n' % (start, end, step)
        content += '    {\n'
        content += '        %s item;\n' % inner_class_type
        for n in range(step):
            field = inner_fields[n]
            origin_type = field['original_type_name']
            typename = lang.map_cpp_type(origin_type)
            content += '        item.%s = ParseTextAs<%s>(row[i + %d]);\n' % (field['name'], typename, n)
        content += '        %s%s.push_back(item);\n' % (prefix, inner_var_name)
        content += '    }\n'
        return content

    # 生成字段赋值
    def gen_all_field_assign_stmt(self, struct, prefix, tabs):
        content = ''

        inner_class_done = False
        inner_field_names, inner_fields = structutil.get_inner_class_mapped_fields(struct)

        vec_names, vec_name = structutil.get_vec_field_range(struct)
        vec_idx = 0
        space = self.TAB_SPACE * tabs
        for field in struct['fields']:
            if not field['enable']:
                continue
            text = ''
            field_name = field['name']
            idx = field['column_index'] - 1
            assert idx >= 0
            if field_name in inner_field_names:
                if not inner_class_done:
                    inner_class_done = True
                    text += self.gen_inner_class_field_assgin_stmt(struct, prefix)
            else:
                origin_type = field['original_type_name']
                typename = lang.map_cpp_type(origin_type)

                if typename != 'std::string' and field['name'] in vec_names:
                    text += '%s%s%s[%d] = %s;\n' % (
                    space, prefix, vec_name, vec_idx, lang.default_value_by_cpp_type(origin_type))

                if origin_type.startswith('array'):
                    text += self.gen_field_array_assign_stmt(prefix, origin_type, field_name,
                                                                ('row[%d]' % idx), tabs)
                elif origin_type.startswith('map'):
                    text += self.gen_field_map_assgin_stmt(prefix, origin_type, field_name,
                                                              ('row[%d]' % idx), tabs)
                else:
                    if field['name'] in vec_names:
                        text += '%s%s%s[%d] = ParseTextAs<%s>(row[%d]);\n' % (
                        self.TAB_SPACE * (tabs), prefix, vec_name, vec_idx, typename, idx)
                        vec_idx += 1
                    else:
                        text += '%s%s%s = ParseTextAs<%s>(row[%d]);\n' % (
                        self.TAB_SPACE * (tabs), prefix, field_name, typename, idx)
            content += text
        return content

    # class静态函数声明
    def gen_struct_method_declare(self, struct):
        content = ''

        if struct['options'][predef.PredefParseKVMode]:
            content += '    static int ParseFromRows(const std::vector<std::vector<StringPiece>>& rows, %s* ptr);\n' % \
                       struct['name']
            if self.gen_dataload:
                content += '    static int Load(const char* filepath);\n'
                content += '    static const %s* Instance();\n' % struct['name']
            return content

        content += '    static int ParseFromRow(const std::vector<StringPiece>& row, %s* ptr);\n' % struct['name']
        if self.gen_dataload:
            content += '    static int Load(const char* filepath);\n'
            content += '    static const std::vector<%s>* GetData(); \n' % struct['name']

        if predef.PredefGetMethodKeys in struct['options']:
            get_keys = structutil.get_struct_keys(struct, predef.PredefGetMethodKeys, lang.map_cpp_type)
            if len(get_keys) > 0:
                get_args = []
                for tpl in get_keys:
                    typename = tpl[0]
                    if not lang.is_cpp_pod_type(typename):
                        typename = 'const %s&' % typename
                    get_args.append(typename + ' ' + tpl[1])

                content += '    static const %s* Get(%s);\n' % (struct['name'], ', '.join(get_args))

        if predef.PredefRangeMethodKeys in struct['options']:
            range_keys = structutil.get_struct_keys(struct, predef.PredefRangeMethodKeys, lang.map_cpp_type)
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
            content += cpp_template.CPP_INSTANCE_METHOD_TEMPLATE % (struct['name'], struct['name'], varname, varname)
        else:
            content += cpp_template.CPP_GETDATA_METHOD_TEMPLATE % (struct['name'], struct['name'], varname, varname)
        return content

    # 生成KV模式的Parse方法
    def gen_kv_parse_method(self, struct):
        rows = struct['data_rows']
        keycol = struct['options'][predef.PredefKeyColumn]
        valcol = struct['options'][predef.PredefValueColumn]
        typcol = int(struct['options'][predef.PredefValueTypeColumn])
        assert keycol > 0 and valcol > 0 and typcol > 0

        keyidx = keycol - 1
        validx = valcol - 1
        typeidx = typcol - 1

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
            text = ''
            if origin_typename.startswith('array'):
                text += self.gen_field_array_assign_stmt('ptr->', origin_typename, name, row_name, 1)
            elif origin_typename.startswith('map'):
                text += self.gen_field_map_assgin_stmt('ptr->', origin_typename, name, row_name, 1)
            else:
                text += '%sptr->%s = ParseTextAs<%s>(%s);\n' % (self.TAB_SPACE, name, typename, row_name)
            idx += 1
            content += text
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
        varname = self.get_instance_data_name(struct['name'])
        content = ''
        content += cpp_template.CPP_KV_LOAD_FUNC_TEMPLATE % (struct['name'], struct['name'],
                                                             self.config_manager_name,
                                                             struct['name'], struct['name'], struct['name'],
                                                             varname, varname)
        content += '\n'
        return content

    # 生成Load()方法
    def gen_struct_load_method(self, struct):
        content = ''
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_struct_load_method(struct)

        varname = self.get_instance_data_name(struct['name'])
        content += cpp_template.CPP_LOAD_FUNC_TEMPLATE % (struct['name'], struct['name'], struct['name'], struct['name'],
                                               self.config_manager_name, struct['name'], struct['name'],
                                               varname, varname)
        content += '\n'
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

        keys = structutil.get_struct_keys(struct, predef.PredefGetMethodKeys, lang.map_cpp_type)
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

        cond_text = self.gen_equal_stmt('dataptr->at(i).', struct, predef.PredefGetMethodKeys)
        content += cpp_template.CPP_GET_METHOD_TEMPLATE % (struct['name'], struct['name'], ', '.join(formal_param),
                                                           struct['name'], cond_text)
        return content

    # 生成GetRange()方法
    def gen_struct_range_method(self, struct):
        content = ''
        if struct['options'][predef.PredefParseKVMode]:
            return content

        if predef.PredefRangeMethodKeys not in struct['options']:
            return content

        keys = structutil.get_struct_keys(struct, predef.PredefRangeMethodKeys, lang.map_cpp_type)
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

        cond_text = self.gen_equal_stmt('dataptr->at(i).', struct, predef.PredefRangeMethodKeys)
        content += cpp_template.CPP_GET_RANGE_METHOD_TEMPLATE % (struct['name'], struct['name'], ', '.join(formal_param),
                                                                 struct['name'], struct['name'], cond_text)
        return content

    # 生成全局Load和Clear方法
    def gen_manager_static_method(self, descriptors):
        if not self.gen_dataload:
            return ''
        content = ''
        content += 'void %s::LoadAll()\n' % self.config_manager_name
        content += '{\n'
        content += '    ASSERT(reader);\n'
        for struct in descriptors:
            filename = strutil.camel_to_snake(struct['camel_case_name'])
            content += '    %s::Load("%s.csv");\n' % (struct['name'], filename)
        content += '}\n\n'

        content += 'void %s::ClearAll()\n' % self.config_manager_name
        content += '{\n'
        for struct in descriptors:
            content += '    delete %s;\n' % self.get_instance_data_name(struct['name'])
            content += '    %s = nullptr;\n' % self.get_instance_data_name(struct['name'])
        content += '}\n\n'

        content += cpp_template.CPP_READ_FUNC_TEMPLATE % self.config_manager_name
        return content

    # 生成源文件定义
    def gen_cpp_source(self, struct):
        content = ''
        if self.gen_dataload:
            content += self.gen_struct_data_method(struct)
            content += self.gen_struct_get_method(struct)
            content += self.gen_struct_range_method(struct)
            content += self.gen_struct_load_method(struct)
        content += self.gen_parse_method(struct)
        return content

    def gen_global_class(self):
        content = ''
        content += cpp_template.CPP_CSV_TOKEN_TEMPLATE % (self.out_csv_delim, '"', self.array_delim[0],
                                                        self.map_delims[0], self.map_delims[1])
        if self.gen_dataload:
            content += 'class %s\n' % self.config_manager_name
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
        cpp_content = '// This file is auto-generated by Tabular v%s, DO NOT EDIT!\n\n' % version.VER_STRING
        if args.cpp_pch is not None:
            pchfile = '#include "%s"' % args.cpp_pch
            cpp_include_headers = [pchfile] + cpp_include_headers

        if self.gen_dataload:
            cpp_include_headers.append('#include "Utility/CSVReader.h"')

        cpp_content += '\n'.join(cpp_include_headers) + '\n\n'
        cpp_content += 'using namespace std;\n\n'
        cpp_content += '#ifndef ASSERT\n'
        cpp_content += '#define ASSERT assert\n'
        cpp_content += '#endif\n\n'


        if args.package is not None:
            cpp_content += '\nnamespace %s\n{\n\n' % args.package

        static_var_content = ''
        if self.gen_dataload:
            cpp_content += cpp_template.CPP_READER_ASSIGN % (self.config_manager_name, self.config_manager_name)
            static_var_content += 'namespace \n{\n'
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

