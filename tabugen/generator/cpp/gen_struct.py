# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import sys
from argparse import Namespace
import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.version as version
import tabugen.util.helper as helper
from tabugen.util.tableutil import legacy_kv_type
from tabugen.structs import Struct, StructField, ArrayField
from tabugen.generator.cpp.gen_csv_load import CppCsvLoadGenerator


# C++代码生成器
class CppStructGenerator:
    TAB_SPACE = '    '

    @staticmethod
    def name():
        return "cpp"

    def __init__(self):
        self.load_gen = None

    def enable_gen_parse(self, name):
        if name is not None:
            if name == 'csv':
                self.load_gen = CppCsvLoadGenerator()
            else:
                print('content loader of name %s not implemented' % name)
                sys.exit(1)

    # 生成字段定义
    def gen_field_define(self, field: StructField, max_type_len: int, max_name_len: int, tabs: int) -> str:
        typename = lang.map_cpp_type(field.origin_type_name)
        assert typename != "", field.origin_type_name
        typename = helper.pad_spaces(typename, max_type_len + 1)
        name = lang.name_with_default_cpp_value(field, typename, False)
        name = helper.pad_spaces(name, max_name_len + 8)
        space = self.TAB_SPACE * tabs
        return '%s%s %s // %s\n' % (space, typename, name, field.comment)

    def gen_array_define(self, field: ArrayField, max_type_len: int, max_name_len: int, tabs: int) -> str:
        name = helper.camel_case(field.field_name)
        name = helper.pad_spaces(name + ';', max_name_len + 4)
        typename = lang.map_cpp_type(field.type_name)
        typename = helper.pad_spaces(typename, max_type_len + 4)
        text = ''
        space = self.TAB_SPACE * tabs
        text += '%s%s %s' % (space, typename, name)
        if field.comment:
            text += ' // %s' % field.comment
        text += '\n'
        return text

    #
    def gen_kv_fields(self, struct: Struct, tabs: int, args: Namespace) -> str:
        space = self.TAB_SPACE * tabs
        key_idx = struct.get_column_index(predef.PredefKVKeyName)
        assert key_idx >= 0
        type_idx = struct.get_column_index(predef.PredefKVTypeName)
        comment_idx = struct.get_kv_comment_col()

        max_name_len, max_type_len = struct.get_kv_max_len(lang.map_cpp_type)
        content = 'struct %s {\n' % struct.camel_case_name
        for row in struct.data_rows:
            key = row[key_idx]
            typename = 'int'
            if type_idx >= 0:
                typename = row[type_idx]
            if key == '' or typename == '':
                continue

            if args.legacy and typename.isdigit():
                typename = legacy_kv_type(int(typename))

            typename = lang.map_cpp_type(typename)
            key_name = helper.pad_spaces(helper.camel_case(key) + ';', max_name_len + 4)
            typename = helper.pad_spaces(typename, max_type_len + 4)
            content += '%s%s %s' % (space, typename, key_name)
            if comment_idx >= 0:
                comment = row[comment_idx].strip()
                comment = comment.replace('\n', ' ')
                comment = comment.replace('//', '')
                if len(content) > 0:
                    content += '\t// %s' % comment
            content += '\n'

        return content

    # 生成class的结构定义
    def gen_struct_define(self, struct: Struct, args: Namespace) -> str:
        content = ''
        if struct.comment:
            content += '// %s, ' % struct.comment
        else:
            content += '// %s, ' % struct.name
        content += ' Created from %s\n' % struct.filepath

        if struct.options[predef.PredefParseKVMode]:
            return content + self.gen_kv_fields(struct, 1, args)

        content += 'struct %s \n{\n' % struct.camel_case_name

        fields = struct.fields
        max_name_len = struct.max_field_name_length()
        max_type_len = struct.max_field_type_length(lang.map_cpp_type)

        for col, field in enumerate(fields):
            text = self.gen_field_define(field, max_type_len, max_name_len, 1)
            content += text
        for array in struct.array_fields:
            content += self.gen_array_define(array, max_type_len, max_name_len, 1)

        return content

    # 生成头文件声明
    def gen_header(self, struct: Struct, args: Namespace) -> str:
        content = ''
        content += self.gen_struct_define(struct, args)
        if self.load_gen is not None:
            content += '\n'
            content += self.load_gen.gen_method_declare(struct)
        content += '};\n\n'
        return content

    # 生成.h头文件内容
    def generate(self, descriptors: list[Struct], args: Namespace):
        h_include_headers = [
            '#include <stdint.h>',
            '#include <string>',
            '#include <vector>',
            '#include <unordered_map>',
            '#include <functional>',
        ]
        if self.load_gen:
            h_include_headers.append('#include "rapidcsv.h"')

        header_content = '// This file is auto-generated by Tabugen v%s, DO NOT EDIT!\n\n#pragma once\n\n' % version.VER_STRING
        header_content += '\n'.join(h_include_headers) + '\n\n'

        if args.package:
            header_content += '\nnamespace %s {\n\n' % args.package

        header_content += 'using std::vector;\n'
        header_content += 'using std::string;\n'
        header_content += 'using std::unordered_map;\n'
        if self.load_gen:
            header_content += 'using rapidcsv::Document;\n'
        header_content += '\n'

        for struct in descriptors:
            header_content += self.gen_header(struct, args)

        if args.package is not None:
            header_content += '} // namespace %s\n' % args.package
        return header_content

    def run(self, descriptors: list[Struct], filepath: str, args: Namespace):
        outname = os.path.split(filepath)[-1]

        cpp_content = ''
        if self.load_gen is not None:
            self.load_gen.setup('')
            filename = outname + '.h'
            cpp_content = self.load_gen.generate(descriptors, args, filename)

        header_content = self.generate(descriptors, args)

        if os.path.isdir(filepath):
            filepath += '/config'
        header_filepath = filepath + '.h'
        filename = os.path.abspath(header_filepath)
        helper.save_content_if_not_same(filename, header_content, args.source_file_encoding)
        print('wrote C++ header file to', filename)

        if len(cpp_content) > 0:
            source_filepath = filepath + '.cpp'
            filename = os.path.abspath(source_filepath)
            modified = helper.save_content_if_not_same(filename, cpp_content, args.source_file_encoding)
            if modified:
                print('wrote C++ source file to', filename)
            else:
                print('file content not modified', filename)

