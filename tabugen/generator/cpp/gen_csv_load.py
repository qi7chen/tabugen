# Copyright (C) 2018-present qi7chen@github. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
from argparse import Namespace
import tabugen.typedef as types
import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.version as version
import tabugen.util.tableutil as tableutil
from tabugen.structs import Struct, StructField, ArrayField


# 生成C++加载CSV文件数据代码
class CppCsvLoadGenerator:
    TAB_SPACE = '    '

    def __init__(self):
        pass

    def setup(self, name):
        pass

    # 生成字段赋值语句
    def gen_field_assign1(self, prefix: str, origin_typename: str, field_name: str, value_text: str, tabs: int) -> str:
        content = ''
        space = self.TAB_SPACE * tabs
        if types.is_array_type(origin_typename):
            cpp_type = lang.map_cpp_type(types.array_element_type(origin_typename))
            content += '%s%s%s = ParseArrayField<%s>(%s);\n' % (space, prefix, field_name, cpp_type, value_text)
        elif types.is_map_type(origin_typename):
            (key_type, val_type) = types.map_key_value_types(origin_typename)
            cpp_type1 = lang.map_cpp_type(key_type)
            cpp_type2 = lang.map_cpp_type(val_type)
            content += '%s%s%s = ParseMapField<%s,%s>(%s);\n' % (space, prefix, field_name, cpp_type1, cpp_type2, value_text)
        else:
            cpp_type = lang.map_cpp_type(origin_typename)
            if value_text == field_name:
                value_text = '"%s"' % value_text
            content += '%s%s%s = ParseField<%s>(%s);\n' % (space, prefix, field_name, cpp_type, value_text)
        return content

    def gen_field_assign2(self, prefix: str, origin_typename: str, field_name: str,  tabs: int) -> str:
        content = ''
        space = self.TAB_SPACE * tabs
        if types.is_array_type(origin_typename):
            cpp_type = lang.map_cpp_type(types.array_element_type(origin_typename))
            value_text = 'GetCellByName<string>(doc, "%s", rowIndex)' % field_name
            content += '%s%s%s = ParseArrayField<%s>(%s);\n' % (space, prefix, field_name, cpp_type, value_text)
        elif types.is_map_type(origin_typename):
            (key_type, val_type) = types.map_key_value_types(origin_typename)
            cpp_type1 = lang.map_cpp_type(key_type)
            cpp_type2 = lang.map_cpp_type(val_type)
            value_text = 'GetCellByName<string>(doc, "%s", rowIndex)' % field_name
            content += '%s%s%s = ParseMapField<%s,%s>(%s);\n' % (space, prefix, field_name, cpp_type1, cpp_type2, value_text)
        else:
            cpp_type = lang.map_cpp_type(origin_typename)
            content += '%s%s%s = GetCellByName<%s>(doc, "%s", rowIndex);\n' % (space, prefix, field_name, cpp_type, field_name)
        return content

    # 生成`ParseFrom`方法
    def gen_parse_method(self, struct: Struct, args: Namespace) -> str:
        content = ''

        content += 'int %s::ParseRow(const Document& doc, int rowIndex, %s* ptr) {\n' % (struct.name, struct.name)
        content += '    ASSERT(ptr != nullptr);\n'
        for field in struct.fields:
            origin_typename = field.origin_type_name
            content += self.gen_field_assign2('ptr->', origin_typename, field.name, 1)

        space = self.TAB_SPACE * 1
        for array in struct.array_fields:
            content += '%sfor (size_t col = 0; col < doc.GetColumnCount(); col++) {\n' % space
            content += '%s    const string& name = stringPrintf("%s[%%d]", col);\n' % (space, array.name)
            content += '%s    int idx = doc.GetColumnIdx(name);\n' % space
            content += '%s    if (idx < 0) {\n' % space
            content += '%s        break;\n' % space
            content += '%s    }\n' % space
            origin_typename = array.element_fields[0].origin_type_name
            cpp_type = lang.map_cpp_type(origin_typename)
            content += '%s    auto elem = GetCellByName<%s>(doc, name, rowIndex);\n' % (space, cpp_type)
            content += '%s    ptr->%s.push_back(elem);\n' % (space, array.field_name)
            content += '%s}\n' % space

        content += '    return 0;\n'
        content += '}\n\n'
        return content

    # 生成KV模式的`ParseFrom`方法
    def gen_kv_parse_method(self, struct: Struct, args: Namespace):
        keyidx = struct.get_column_index(predef.PredefKVKeyName)
        typeidx = struct.get_column_index(predef.PredefKVTypeName)

        content = ''
        content += 'int %s::ParseFrom(const unordered_map<string,string>& table, %s* ptr) {\n' % (struct.name, struct.name)
        content += '    ASSERT(ptr != nullptr);\n'
        rows = struct.data_rows
        for row in rows:
            name = row[keyidx].strip()
            origin_typename = row[typeidx].strip()
            if args.legacy:
                try:
                    legacy = int(origin_typename)
                    origin_typename = types.legacy_type_to_name(legacy)
                except ValueError:
                    pass
            valuetext = 'GetTableField(table, "%s")' % name
            content += self.gen_field_assign1('ptr->', origin_typename, name, valuetext, 1)
        content += '    return 0;\n'
        content += '}\n\n'
        return content

    # 生成源文件定义
    def gen_cpp_source(self, struct: Struct, args: Namespace) -> str:
        if struct.options[predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct, args)
        else:
            return self.gen_parse_method(struct, args)

    # class静态函数声明
    def gen_method_declare(self, struct: Struct) -> str:
        content = ''
        if struct.options[predef.PredefParseKVMode]:
            content += '    static int ParseFrom(const unordered_map<string,string>& table, %s* ptr);\n' % struct.name
            return content
        content += '    static int ParseRow(const Document& doc, int rowIndex, %s* ptr);\n' % struct.name
        return content

    def generate(self, descriptors: list[Struct], args: Namespace, headerfile: str) -> str:
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
        if args.cpp_pch:
            pchfile = '#include "%s"' % args.cpp_pch
            cpp_include_headers = [pchfile] + cpp_include_headers

        cpp_content += '\n'.join(cpp_include_headers) + '\n\n'
        cpp_content += 'using namespace std;\n'
        cpp_content += 'using rapidcsv::Document;\n\n'
        cpp_content += '#ifndef ASSERT\n'
        cpp_content += '#define ASSERT assert\n'
        cpp_content += '#endif\n\n'

        if args.package is not None:
            cpp_content += '\nnamespace %s {\n\n' % args.package

        class_content = ''
        for struct in descriptors:
            class_content += self.gen_cpp_source(struct, args)

        cpp_content += class_content
        if args.package is not None:
            cpp_content += '\n} // namespace %s \n' % args.package  # namespace
        return cpp_content
