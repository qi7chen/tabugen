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
        self.config_manager_name = ''

    # 初始化
    def setup(self, name):
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
        space = self.TAB_SPACE * (tabs + 1)
        elemt_type = lang.map_cpp_type(types.array_element_type(typename))
        content = '%s{\n' % (self.TAB_SPACE * tabs)
        content += '%sconst std::vector<absl::string_view>& array = absl::StrSplit(%s, "%s");\n' % (space, row_name, predef.PredefDelim1)
        content += '%sfor (size_t i = 0; i < array.size(); i++)\n' % space
        content += '%s{\n' % space
        content += '%s    %s%s.push_back(to<%s>(array[i]));\n' % (space, prefix, name, elemt_type)
        content += '%s}\n' % space
        content += '%s}\n' % (self.TAB_SPACE * tabs)
        return content

    # map赋值
    def gen_field_map_assgin_stmt(self, prefix, typename, name, row_name, tabs):
        k, v = types.map_key_value_types(typename)
        key_type = lang.map_cpp_type(k)
        val_type = lang.map_cpp_type(v)
        space = self.TAB_SPACE * (tabs + 1)
        content = '%s{\n' % (self.TAB_SPACE * tabs)
        content += '%sconst std::vector<absl::string_view>& vec = absl::StrSplit(%s, "%s");\n' % (space, row_name, predef.PredefDelim1)
        content += '%sfor (size_t i = 0; i < vec.size(); i++)\n' % space
        content += '%s{\n' % space
        content += '%s    const std::vector<absl::string_view>& kv = absl::StrSplit(vec[i], "%s");\n' % (space, predef.PredefDelim2)
        content += '%s    ASSERT(kv.size() == 2);\n' % space
        content += '%s    if(kv.size() == 2)\n' % space
        content += '%s    {\n' % space
        content += '%s        const auto& key = to<%s>(kv[0]);\n' % (space, key_type)
        content += '%s        ASSERT(%s%s.count(key) == 0);\n' % (space, prefix, name)
        content += '%s        %s%s[key] = to<%s>(kv[1]);\n' % (space, prefix, name, val_type)
        content += '%s    }\n' % space
        content += '%s}\n' % space
        content += '%s}\n' % (self.TAB_SPACE * tabs)
        return content

    # 内部class赋值
    def gen_inner_field_assign(self, struct, prefix, rec_name, tabs):
        inner_fields = struct['inner_fields']
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerFieldName]
        assert len(inner_class_type) > 0 and len(inner_var_name) > 0

        start = inner_fields['start']
        end = inner_fields['end']
        step = inner_fields['step']
        assert start > 0 and end > 0 and step > 1

        space = self.TAB_SPACE * tabs
        col = start
        content = ''
        content += '%sfor (int i = 1; i <= %d; i++)\n' % (space, (end-start)/step)
        content += '%s{\n' % space
        content += '%s    %s::%s val;\n' % (space, struct['camel_case_name'], inner_class_type)
        for i in range(step):
            field = struct['fields'][col + i]
            origin_type = field['original_type_name']
            typename = lang.map_cpp_type(origin_type)
            field_name = strutil.remove_suffix_number(field['camel_case_name'])
            valuetext = '%s[to<std::string>("%s", i)]' % (rec_name, field_name)
            content += '        val.%s = to<%s>(%s);\n' % (field_name, typename, valuetext)
        content += '        %s%s.push_back(val);\n' % (prefix, inner_var_name)
        content += '%s}\n' % space
        return content

    # 生成字段赋值
    def gen_field_assign(self, field, prefix, value_text, tabs):
        text = ''
        origin_type = field['original_type_name']
        typename = lang.map_cpp_type(origin_type)
        field_name = field['name']
        if origin_type.startswith('array'):
            text += self.gen_field_array_assign_stmt(prefix, origin_type, field_name, value_text, tabs)
        elif origin_type.startswith('map'):
            text += self.gen_field_map_assgin_stmt(prefix, origin_type, field_name, value_text, tabs)
        else:
            text += '%s%s%s = to<%s>(%s);\n' % (
                self.TAB_SPACE * tabs, prefix, field_name, typename, value_text)
        return text

    # class静态函数声明
    def gen_struct_method_declare(self, struct):
        content = ''

        if struct['options'][predef.PredefParseKVMode]:
            content += '    static int ParseFrom(std::unordered_map<std::string, std::string>& fields, %s* ptr);\n' % \
                       struct['name']
            return content

        content += '    static int ParseFrom(std::unordered_map<std::string, std::string>& fields, %s* ptr);\n' % struct['name']

        return content

    # 生成KV模式的Parse方法
    def gen_kv_parse_method(self, struct):
        keyidx = predef.PredefKeyColumn
        validx = predef.PredefValueColumn
        typeidx = predef.PredefValueTypeColumn
        assert keyidx >= 0 and validx >= 0 and typeidx >= 0

        rows = struct['data_rows']
        content = ''
        content += '// parse data object from record\n'
        content += 'int %s::ParseFrom(std::unordered_map<std::string, std::string>& fields, %s* ptr)\n' % (
            struct['name'], struct['name'])
        content += '{\n'
        content += '    ASSERT(ptr != nullptr);\n'
        idx = 0
        for row in rows:
            name = row[keyidx].strip()
            origin_typename = row[typeidx].strip()
            typename = lang.map_cpp_type(origin_typename)
            value_text = 'fields["%s"]' % name
            text = ''
            if origin_typename.startswith('array'):
                text += self.gen_field_array_assign_stmt('ptr->', origin_typename, name, value_text, 1)
            elif origin_typename.startswith('map'):
                text += self.gen_field_map_assgin_stmt('ptr->', origin_typename, name, value_text, 1)
            else:
                text += '%sptr->%s = to<%s>(%s);\n' % (self.TAB_SPACE, name, typename, value_text)
            idx += 1
            content += text
        content += '    return 0;\n'
        content += '}\n\n'
        return content

    # 生成ParseFrom方法
    def gen_parse_method(self, struct):
        content = ''
        inner_start_col = -1
        inner_end_col = -1
        inner_field_done = False
        if 'inner_fields' in struct:
            inner_start_col = struct['inner_fields']['start']
            inner_end_col = struct['inner_fields']['end']

        content += '// parse data object from an csv row\n'
        content += 'int %s::ParseFrom(std::unordered_map<std::string, std::string>& record, %s* ptr)\n' % (struct['name'], struct['name'])
        content += '{\n'
        content += '    ASSERT(ptr != nullptr);\n'

        for col, field in enumerate(struct['fields']):
            if inner_start_col <= col < inner_end_col:
                if not inner_field_done:
                    inner_field_done = True
                    content += self.gen_inner_field_assign(struct, 'ptr->', 'record', 1)
            else:
                value_text = 'record["%s"]' % field['name']
                content += self.gen_field_assign(field, 'ptr->', value_text, 1)

        content += '    return 0;\n'
        content += '}\n\n'
        return content

    # 生成源文件定义
    def gen_cpp_source(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct)
        else:
            return self.gen_parse_method(struct)

    def generate(self, descriptors, args, headerfile):
        extra_include = '#include "{}"'.format(args.extra_cpp_include)
        cpp_include_headers = [
            '#include "%s"' % os.path.basename(headerfile),
            '#include <stddef.h>',
            '#include <assert.h>',
            '#include <memory>',
            '#include <fstream>',
            extra_include,
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
