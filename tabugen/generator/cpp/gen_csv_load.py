# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import tabugen.typedef as types
import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.version as version
import tabugen.util.strutil as strutil
import tabugen.util.structutil as structutil
import tabugen.generator.cpp.template as cpp_template


# 生成C++加载CSV文件数据代码
class CppCsvLoadGenerator:
    TAB_SPACE = '    '

    def __init__(self):
        self.array_delim = ','
        self.map_delims = [',', '=']
        self.out_csv_delim = ','
        self.config_manager_name = ''

    # 初始化array, map分隔符
    def setup(self, array_delim, map_delims, out_csv_delim, name):
        self.array_delim = array_delim
        self.map_delims = map_delims
        self.out_csv_delim = out_csv_delim
        self.config_manager_name = name

    @staticmethod
    def get_instance_data_name(name):
        return '_instance_%s' % name.lower()

    # 生成赋值表达式
    @staticmethod
    def gen_equal_stmt(prefix, struct, key):
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
        content += '%sconst std::vector<absl::string_view>& array = absl::StrSplit(%s, TABULAR_ARRAY_DELIM);\n' % (space, row_name)
        content += '%sfor (size_t i = 0; i < array.size(); i++)\n' % space
        content += '%s{\n' % space
        content += '%s    %s%s.push_back(parseStrAs<%s>(array[i]));\n' % (space, prefix, name, elemt_type)
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
        content += '%sconst std::vector<absl::string_view>& vec = absl::StrSplit(%s, TABULAR_MAP_DELIM1);\n' % (space, row_name)
        content += '%sfor (size_t i = 0; i < vec.size(); i++)\n' % space
        content += '%s{\n' % space
        content += '%s    const std::vector<absl::string_view>& kv = absl::StrSplit(vec[i], TABULAR_MAP_DELIM2);\n' % space
        content += '%s    ASSERT(kv.size() == 2);\n' % space
        content += '%s    if(kv.size() == 2)\n' % space
        content += '%s    {\n' % space
        content += '%s        const auto& key = parseStrAs<%s>(kv[0]);\n' % (space, key_type)
        content += '%s        ASSERT(%s%s.count(key) == 0);\n' % (space, prefix, name)
        content += '%s        %s%s[key] = parseStrAs<%s>(kv[1]);\n' % (space, prefix, name, val_type)
        content += '%s    }\n' % space
        content += '%s}\n' % space
        content += '%s}\n' % (self.TAB_SPACE * tabs)
        return content

    # 内部class赋值
    @staticmethod
    def gen_inner_class_field_assgin_stmt(struct, prefix):
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
            content += '        item.%s = parseStrAs<%s>(row[i + %d]);\n' % (field['name'], typename, n)
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
        idx = 0
        space = self.TAB_SPACE * tabs
        for field in struct['fields']:
            if not field['enable']:
                continue
            text = ''
            field_name = field['name']
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
                        text += '%s%s%s[%d] = parseStrAs<%s>(row[%d]);\n' % (
                            self.TAB_SPACE * tabs, prefix, vec_name, vec_idx, typename, idx)
                        vec_idx += 1
                    else:
                        text += '%s%s%s = parseStrAs<%s>(row[%d]);\n' % (
                            self.TAB_SPACE * tabs, prefix, field_name, typename, idx)
            idx += 1
            content += text
        return content

    # class静态函数声明
    def gen_struct_method_declare(self, struct):
        content = ''

        if struct['options'][predef.PredefParseKVMode]:
            content += '    static int ParseFromRows(const std::vector<CSVRow>& rows, %s* ptr);\n' % \
                       struct['name']
            return content

        content += '    static int ParseFromRow(const CSVRow& row, %s* ptr);\n' % struct['name']

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
        content += 'int %s::ParseFromRows(const vector<CSVRow>& rows, %s* ptr)\n' % (
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
                text += '%sptr->%s = parseStrAs<%s>(%s);\n' % (self.TAB_SPACE, name, typename, row_name)
            idx += 1
            content += text
        content += '    return 0;\n'
        content += '}\n\n'
        return content

    # 生成ParseFromRow方法
    def gen_parse_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct)

        fields = structutil.enabled_fields(struct)
        content = ''
        content += '// parse data object from an csv row\n'
        content += 'int %s::ParseFromRow(const CSVRow& row, %s* ptr)\n' % (struct['name'], struct['name'])
        content += '{\n'
        content += '    ASSERT(row.size() >= %d);\n' % len(fields)
        content += '    ASSERT(ptr != nullptr);\n'
        content += self.gen_all_field_assign_stmt(struct, 'ptr->', 1)
        content += '    return 0;\n'
        content += '}\n\n'
        return content


    # 生成源文件定义
    def gen_cpp_source(self, struct):
        content = ''
        content += self.gen_parse_method(struct)
        return content

    def gen_global_class(self):
        content = ''
        # 常量定义在头文件，方便外部解析使用
        content += cpp_template.CPP_CSV_TOKEN_TEMPLATE % (self.out_csv_delim, '"', self.array_delim[0],
                                                          self.map_delims[0], self.map_delims[1])
        return content

    def gen_source_method(self, descriptors, args, headerfile):
        cpp_include_headers = [
            '#include "%s"' % os.path.basename(headerfile),
            '#include <stddef.h>',
            '#include <assert.h>',
            '#include <memory>',
            '#include <fstream>',
            '#include <absl/strings/str_split.h>',
        ]
        cpp_content = '// This file is auto-generated by Tabular v%s, DO NOT EDIT!\n\n' % version.VER_STRING
        if args.cpp_pch is not None:
            pchfile = '#include "%s"' % args.cpp_pch
            cpp_include_headers = [pchfile] + cpp_include_headers

        cpp_content += '\n'.join(cpp_include_headers) + '\n\n'
        cpp_content += 'using namespace std;\n\n'
        cpp_content += '#ifndef ASSERT\n'
        cpp_content += '#define ASSERT assert\n'
        cpp_content += '#endif\n\n'

        if args.package is not None:
            cpp_content += '\nnamespace %s {\n\n' % args.package

        static_var_content = ''

        class_content = ''
        for struct in descriptors:
            class_content += self.gen_cpp_source(struct)

        cpp_content += static_var_content
        cpp_content += class_content
        if args.package is not None:
            cpp_content += '\n} // namespace %s \n' % args.package  # namespace
        return cpp_content