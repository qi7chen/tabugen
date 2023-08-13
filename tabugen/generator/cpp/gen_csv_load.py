# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import tabugen.typedef as types
import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.version as version
import tabugen.util.tableutil as tableutil


# 生成C++加载CSV文件数据代码
class CppCsvLoadGenerator:
    TAB_SPACE = '    '

    def __init__(self):
        pass

    def setup(self, name):
        pass

    # 生成字段赋值语句
    def gen_field_assign(self, prefix: str, origin_typename: str, field_name: str, rec_name: str, value_text: str, tabs: int) -> str:
        content = ''
        space = self.TAB_SPACE * tabs
        if types.is_array_type(origin_typename):
            cpp_type = lang.map_cpp_type(types.array_element_type(origin_typename))
            content += '%s%s%s = parseArrayField<%s>(%s, "%s");\n' % (space, prefix, field_name, cpp_type, rec_name, value_text)
        elif types.is_map_type(origin_typename):
            (key_type, val_type) = types.map_key_value_types(origin_typename)
            cpp_type1 = lang.map_cpp_type(key_type)
            cpp_type2 = lang.map_cpp_type(val_type)
            content += '%s%s%s = parseMapField<%s,%s>(%s, "%s");\n' % (space, prefix, field_name, cpp_type1, cpp_type2, rec_name, value_text)
        else:
            cpp_type = lang.map_cpp_type(origin_typename)
            if value_text == field_name:
                value_text = '"%s"' % value_text
            content += '%s%s%s = parseField<%s>(%s, %s);\n' % (space, prefix, field_name, cpp_type, rec_name, value_text)
        return content

    # 内部嵌入class的赋值
    def gen_inner_fields_assign(self, struct, prefix: str, rec_name: str, tabs: int) -> str:
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
        content += '%sfor (size_t i = 0; i < %s.size(); i++)\n' % (space, rec_name)
        content += '%s{\n' % space
        content += '%s    %s::%s val;\n' % (space, struct['camel_case_name'], inner_class_type)
        for i in range(step):
            field = struct['fields'][col + i]
            origin_typename = field['original_type_name']
            field_name = tableutil.remove_field_suffix(field['camel_case_name'])
            text = '%s    {\n' % space
            text += '%s        auto key = stringPrintf("%s[%%d]", i);\n' % (space, field_name)
            if i == 0:
                text += '%s        auto iter = %s.find(key);\n' % (space, rec_name)
                text += '%s        if (iter == %s.end()) {\n' % (space, rec_name)
                text += '%s            break;\n' % space
                text += '%s        }\n' % space
            text += self.gen_field_assign('val.', origin_typename, field_name, rec_name, "key", tabs + 2)
            text += '%s    }\n' % space
            content += text
        content += '        %s%s.push_back(val);\n' % (prefix, inner_var_name)
        content += '%s}\n' % space
        content += '%s%s%s.shrink_to_fit();\n' % (space, prefix, inner_var_name)
        return content

    # 生成`ParseFrom`方法
    def gen_parse_method(self, struct) -> str:
        content = ''
        inner_start_col = -1
        inner_end_col = -1
        inner_field_done = False
        if 'inner_fields' in struct:
            inner_start_col = struct['inner_fields']['start']
            inner_end_col = struct['inner_fields']['end']

        content += '// parse %s from string fields\n' % struct['name']
        content += 'int %s::ParseFrom(const unordered_map<string, string>& record, %s* ptr)\n' % (struct['name'], struct['name'])
        content += '{\n'
        content += '    ASSERT(ptr != nullptr);\n'
        for col, field in enumerate(struct['fields']):
            if inner_start_col <= col <= inner_end_col:
                if not inner_field_done:
                    inner_field_done = True
                    content += self.gen_inner_fields_assign(struct, 'ptr->', 'record', 1)
            else:
                origin_typename = field['original_type_name']
                content += self.gen_field_assign('ptr->', origin_typename, field['name'], 'record', field['name'], 1)

        content += '    return 0;\n'
        content += '}\n\n'
        return content

    # 生成KV模式的`ParseFrom`方法
    def gen_kv_parse_method(self, struct):
        keyidx = struct['options']['key_column']
        validx = struct['options']['value_column']
        typeidx = struct['options']['type_column']
        assert keyidx >= 0 and validx >= 0 and typeidx >= 0

        rows = struct['data_rows']
        content = ''
        content += '// parse %s from string fields\n' % struct['name']
        content += 'int %s::ParseFrom(const unordered_map<string, string>& fields, %s* ptr)\n' % (
            struct['name'], struct['name'])
        content += '{\n'
        content += '    ASSERT(ptr != nullptr);\n'
        for row in rows:
            name = row[keyidx].strip()
            origin_typename = row[typeidx].strip()
            content += self.gen_field_assign('ptr->', origin_typename, name, 'fields', name, 1)
        content += '    return 0;\n'
        content += '}\n\n'
        return content

    # 生成源文件定义
    def gen_cpp_source(self, struct) -> str:
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct)
        else:
            return self.gen_parse_method(struct)

    # class静态函数声明
    def generate_method_declare(self, struct) -> str:
        content = ''
        if struct['options'][predef.PredefParseKVMode]:
            content += '    static int ParseFrom(const std::unordered_map<std::string, std::string>& fields, %s* ptr);\n' % struct['name']
            return content
        content += '    static int ParseFrom(const std::unordered_map<std::string, std::string>& fields, %s* ptr);\n' % struct['name']
        return content

    def generate(self, descriptors, args, headerfile) -> str:
        cpp_include_headers = [
            '#include "%s"' % os.path.basename(headerfile),
            '#include <stddef.h>',
            '#include "Conv.h"',
        ]
        if len(args.extra_cpp_includes) > 0:
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

        class_content = ''
        for struct in descriptors:
            class_content += self.gen_cpp_source(struct)

        cpp_content += class_content
        if args.package is not None:
            cpp_content += '\n} // namespace %s \n' % args.package  # namespace
        return cpp_content
