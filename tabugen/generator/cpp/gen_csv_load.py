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
    def gen_array_field_assign(self, prefix, typename, name, value_text, tabs):
        space = self.TAB_SPACE * (tabs + 1)
        parse_fn = lang.map_cpp_parse_fn(types.array_element_type(typename))
        content = '%s{\n' % (self.TAB_SPACE * tabs)
        content += '%sauto arr = SplitString(%s, "%s");\n' % (space, value_text, predef.PredefDelim1)
        content += '%sfor (size_t i = 0; i < arr.size(); i++)\n' % space
        content += '%s{\n' % space
        content += '%s    if (!arr[i].empty()) {\n' % space
        content += '%s        auto val = %s(arr[i]);\n' % (space, parse_fn)
        content += '%s        %s%s.emplace_back(val);\n' % (space, prefix, name)
        content += '%s    }\n' % space
        content += '%s}\n' % space
        content += '%s}\n' % (self.TAB_SPACE * tabs)
        return content

    # map赋值
    def gen_map_field_assign(self, prefix, typename, name, row_name, tabs):
        key_type, val_type = types.map_key_value_types(typename)
        space = self.TAB_SPACE * (tabs + 1)
        content = '%s{\n' % (self.TAB_SPACE * tabs)
        content += '%sauto kvs = SplitString(%s, "%s");\n' % (space, row_name, predef.PredefDelim1)
        content += '%sfor (size_t i = 0; i < kvs.size(); i++)\n' % space
        content += '%s{\n' % space
        content += '%s    auto kv = SplitString(kvs[i], "%s");\n' % (space, predef.PredefDelim2)
        content += '%s    ASSERT(kv.size() == 2);\n' % space
        content += '%s    if(kv.size() == 2)\n' % space
        content += '%s    {\n' % space
        content += '%s        auto key = %s(kv[0]);\n' % (space, lang.map_cpp_parse_fn(key_type))
        content += '%s        auto val = %s(kv[1]);\n' % (space, lang.map_cpp_parse_fn(val_type))
        content += '%s        ASSERT(%s%s.count(key) == 0);\n' % (space, prefix, name)
        content += '%s        %s%s.emplace(std::make_pair(key, val));\n' % (space, prefix, name)
        content += '%s    }\n' % space
        content += '%s}\n' % space
        content += '%s}\n' % (self.TAB_SPACE * tabs)
        return content

    def gen_field_assign(self, prefix: str, origin_typename: str, name: str, value_text: str, tabs: int) -> str:
        content = ''
        space = self.TAB_SPACE * tabs
        if origin_typename.startswith('array'):
            content += self.gen_array_field_assign(prefix, origin_typename, name, value_text, tabs)
        elif origin_typename.startswith('map'):
            content += self.gen_map_field_assign(prefix, origin_typename, name, value_text, tabs)
        elif origin_typename == 'string':
            content += '%s%s%s = %s;\n' % (space, prefix, name, value_text)
        else:
            fn = lang.map_cpp_parse_fn(origin_typename)
            content += '%s%s%s = %s(%s);\n' % (space, prefix, name, fn, value_text)
        return content

    # 内部class赋值
    def gen_inner_fields_assign(self, struct, prefix, rec_name, tabs):
        inner_fields = struct['inner_fields']
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerFieldName]
        assert len(inner_class_type) > 0 and len(inner_var_name) > 0

        start = inner_fields['start']
        end = inner_fields['end']
        step = inner_fields['step']
        count = (end - start) / step
        assert start > 0 and end > 0 and step > 1

        space = self.TAB_SPACE * tabs
        col = start
        content = '%s%s%s.reserve(%d);\n' % (space, prefix, inner_var_name, count)
        content += '%sfor (int i = 1; i <= %d; i++)\n' % (space, count)
        content += '%s{\n' % space
        content += '%s    %s::%s val;\n' % (space, struct['camel_case_name'], inner_class_type)
        content += '%s    std::string key;\n' % space
        for i in range(step):
            field = struct['fields'][col + i]
            origin_typename = field['original_type_name']
            field_name = strutil.remove_suffix_number(field['camel_case_name'])
            valuetext = '%s[StringPrintf("%s%%d", i)]' % (rec_name, field_name)
            content += self.gen_field_assign('val.', origin_typename, field_name, valuetext, tabs + 1)
        content += '        %s%s.push_back(val);\n' % (prefix, inner_var_name)
        content += '%s}\n' % space
        return content

    # 生成KV模式的Parse方法
    def gen_kv_parse_method(self, struct):
        keyidx = predef.PredefKeyColumn
        validx = predef.PredefValueColumn
        typeidx = predef.PredefValueTypeColumn
        assert keyidx >= 0 and validx >= 0 and typeidx >= 0

        rows = struct['data_rows']
        content = ''
        content += '// parse %s from string fields\n' % struct['name']
        content += 'int %s::ParseFrom(std::unordered_map<std::string, std::string>& fields, %s* ptr)\n' % (
            struct['name'], struct['name'])
        content += '{\n'
        content += '    ASSERT(ptr != nullptr);\n'
        for row in rows:
            name = row[keyidx].strip()
            origin_typename = row[typeidx].strip()
            value_text = 'fields["%s"]' % name
            content += self.gen_field_assign('ptr->', origin_typename, name, value_text, 1)
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

        content += '// parse %s from string fields\n' % struct['name']
        content += 'int %s::ParseFrom(std::unordered_map<std::string, std::string>& record, %s* ptr)\n' % (struct['name'], struct['name'])
        content += '{\n'
        content += '    ASSERT(ptr != nullptr);\n'

        for col, field in enumerate(struct['fields']):
            if inner_start_col <= col < inner_end_col:
                if not inner_field_done:
                    inner_field_done = True
                    content += self.gen_inner_fields_assign(struct, 'ptr->', 'record', 1)
            else:
                origin_typename = field['original_type_name']
                value_text = 'record["%s"]' % field['name']
                content += self.gen_field_assign('ptr->', origin_typename, field['name'], value_text, 1)

        content += '    return 0;\n'
        content += '}\n\n'
        return content

    # 生成源文件定义
    def gen_cpp_source(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct)
        else:
            return self.gen_parse_method(struct)

    # class静态函数声明
    def gen_struct_method_declare(self, struct):
        content = ''
        if struct['options'][predef.PredefParseKVMode]:
            content += '    static int ParseFrom(std::unordered_map<std::string, std::string>& fields, %s* ptr);\n' % struct['name']
            return content
        content += '    static int ParseFrom(std::unordered_map<std::string, std::string>& fields, %s* ptr);\n' % struct['name']
        return content

    def generate(self, descriptors, args, headerfile):
        cpp_include_headers = [
            '#include "%s"' % os.path.basename(headerfile),
            '#include <stddef.h>',
            '#include <assert.h>',
            '#include <memory>',
            '#include <fstream>',
        ]
        extra_headers = args.extra_cpp_includes.split(',')
        for header in extra_headers:
            text = '#include "%s"' % header
            cpp_include_headers.append(text)

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
