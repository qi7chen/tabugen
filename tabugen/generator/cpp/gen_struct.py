# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import sys
import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.version as version
import tabugen.util.strutil as strutil
import tabugen.generator.cpp.template as cpp_template
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
    def gen_field_define(self, field, max_type_len: int, max_name_len: int, tabs: int) -> str:
        typename = lang.map_cpp_type(field['original_type_name'])
        assert typename != "", field['original_type_name']
        typename = strutil.pad_spaces(typename, max_type_len + 1)
        name = lang.name_with_default_cpp_value(field, typename, False)
        name = strutil.pad_spaces(name, max_name_len + 8)
        space = self.TAB_SPACE * tabs
        return '%s%s %s // %s\n' % (space, typename, name, field['comment'])

    # 生成嵌入类型的字段定义
    def gen_inner_field_define(self, struct, max_type_len: int, max_name_len: int, tabs: int) -> str:
        type_class_name = strutil.camel_case(struct["options"][predef.PredefInnerTypeClass])
        inner_field_name = struct["options"][predef.PredefInnerFieldName]
        type_name = 'std::vector<%s>' % type_class_name
        type_name = strutil.pad_spaces(type_name, max_type_len + 1)
        inner_field_name = strutil.pad_spaces(inner_field_name, max_name_len + 1)
        assert len(inner_field_name) > 0
        space = self.TAB_SPACE * tabs
        return '%s%s %s;    // \n' % (space, type_name, inner_field_name)

    # 生成嵌入类型定义
    def gen_inner_struct_define(self, struct) -> str:
        inner_fields = struct['inner_fields']
        start = inner_fields['start']
        end = inner_fields['end']
        step = inner_fields['step']
        type_class_name = strutil.camel_case(struct["options"][predef.PredefInnerTypeClass])
        assert len(type_class_name) > 0

        max_name_len = 0
        max_type_len = 0
        for col in range(start, end):
            field = struct['fields'][col]
            name_len = len(field['name'])
            type_len = len(lang.map_cpp_type(field['original_type_name']))
            if name_len > max_name_len:
                max_name_len = name_len
            if type_len > max_type_len:
                max_type_len = type_len

        content = '    struct %s \n' % type_class_name
        content += '    {\n'
        col = start
        while col < start + step:
            field = struct['fields'][col]
            typename = lang.map_cpp_type(field['original_type_name'])
            assert typename != "", field['original_type_name']
            typename = strutil.pad_spaces(typename, max_type_len + 1)
            name = lang.name_with_default_cpp_value(field, typename, True)
            name = strutil.pad_spaces(name, max_name_len + 8)
            content += '        %s %s // %s\n' % (typename, name, field['comment'])
            col += 1
        content += '    };\n'
        return content

    # 生成class的结构定义
    def gen_struct_define(self, struct) -> str:
        content = '// %s\n' % struct['comment']
        content += 'struct %s \n{\n' % struct['camel_case_name']

        inner_start_col = -1
        inner_end_col = -1
        inner_field_done = False
        if 'inner_fields' in struct:
            inner_start_col = struct['inner_fields']['start']
            inner_end_col = struct['inner_fields']['end']
            content += self.gen_inner_struct_define(struct)
            content += '\n'

        fields = struct['fields']
        max_name_len = strutil.max_field_length(fields, 'name', None)
        max_type_len = strutil.max_field_length(fields, 'original_type_name', lang.map_cpp_type)
        if inner_start_col >= 0:
            type_class_name = strutil.camel_case(struct["options"][predef.PredefInnerTypeClass])
            field_name = 'std::vector<%s>' % type_class_name
            if len(field_name) > max_type_len:
                max_type_len = len(field_name)

        for col, field in enumerate(fields):
            text = ''
            if inner_start_col <= col <= inner_end_col:
                if not inner_field_done:
                    text = self.gen_inner_field_define(struct, max_type_len, max_name_len, 1)
                    inner_field_done = True
            else:
                text = self.gen_field_define(field, max_type_len, max_name_len, 1)
            content += text
        return content

    # 生成头文件声明
    def gen_header(self, struct) -> str:
        content = ''
        content += self.gen_struct_define(struct)
        if self.load_gen is not None:
            content += '\n'
            content += self.load_gen.generate_method_declare(struct)
        content += '};\n\n'
        return content

    # 生成.h头文件内容
    def generate(self, descriptors, args):
        h_include_headers = [
            '#include <stdint.h>',
            '#include <string>',
            '#include <vector>',
            '#include <unordered_map>',
            '#include <functional>',
        ]

        header_content = '// This file is auto-generated by Tabugen v%s, DO NOT EDIT!\n\n#pragma once\n\n' % version.VER_STRING
        header_content += '\n'.join(h_include_headers) + '\n\n'

        if args.package is not None:
            header_content += '\nnamespace %s {\n\n' % args.package

        for struct in descriptors:
            print(strutil.current_time(), 'start generate', struct['source'])
            header_content += self.gen_header(struct)

        if args.package is not None:
            header_content += '} // namespace %s\n' % args.package
        return header_content

    def run(self, descriptors, filepath, args):
        outname = os.path.split(filepath)[-1]

        cpp_content = ''
        if self.load_gen is not None:
            self.load_gen.setup('')
            filename = outname + '.h'
            cpp_content = self.load_gen.generate(descriptors, args, filename)

        header_content = self.generate(descriptors, args)

        header_filepath = filepath + '.h'
        filename = os.path.abspath(header_filepath)
        strutil.save_content_if_not_same(filename, header_content, args.source_file_encoding)
        print('wrote C++ header file to', filename)

        if len(cpp_content) > 0:
            source_filepath = filepath + '.cpp'
            filename = os.path.abspath(source_filepath)
            modified = strutil.save_content_if_not_same(filename, cpp_content, args.source_file_encoding)
            if modified:
                print('wrote C++ source file to', filename)
            else:
                print('file content not modified', filename)

        # 3rd party parse API
        if args.with_conv and self.load_gen is not None:
            filename = os.path.join(os.path.split(filepath)[0], 'Conv.h')
            modified = strutil.save_content_if_not_same(filename, cpp_template.CPP_CONV_TEMPLATE, args.source_file_encoding)
            if modified:
                print('wrote 3rd source file to', filename)
