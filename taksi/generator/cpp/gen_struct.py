# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import taksi.predef as predef
import taksi.lang as lang
import taksi.strutil as strutil
import taksi.generator.genutil as genutil
import taksi.version as version
from taksi.generator.cpp.gen_csv_load import CppCsvLoadGenerator


# C++代码生成器
class CppStructGenerator:

    def __init__(self):
        self.load_gen = None

    def init(self, loader_name):
        """
            :param loader_name: loader需要满足2个接口
                gen_struct_method_declare()
                gen_global_class()
                gen_source_method()
        """
        if loader_name is not None:
            if loader_name.strip() == 'csv':
                self.load_gen = CppCsvLoadGenerator()

    @staticmethod
    def name():
        return "cpp"

    # 生成class定义结构，不包含结尾的'}'符号
    def gen_cpp_struct_define(self, struct):
        content = '// %s\n' % struct['comment']
        content += 'struct %s \n{\n' % struct['name']
        fields = struct['fields']
        if struct['options'][predef.PredefParseKVMode]:
            fields = genutil.get_struct_kv_fields(struct)

        inner_class_done = False
        inner_typename = ''
        inner_var_name = ''
        inner_field_names, mapped_inner_fields = genutil.get_inner_class_mapped_fields(struct)
        if len(mapped_inner_fields) > 0:
            content += self.gen_inner_struct_define(struct)
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
    def gen_inner_struct_define(self, struct):
        inner_fields = genutil.get_inner_class_struct_fields(struct)
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

    # 生成头文件声明
    def gen_cpp_header(self, struct):
        content = ''
        content += self.gen_cpp_struct_define(struct)
        if self.load_gen is not None:
            content += '\n'
            content += self.load_gen.gen_struct_method_declare(struct)
        content += '};\n\n'
        return content

    # 生成.h头文件内容
    def gen_header_content(self, descriptors, args):
        h_include_headers = [
            '#include <stdint.h>',
            '#include <string>',
            '#include <vector>',
            '#include <map>',

        ]
        if self.load_gen is not None:
            other_headers = [
                '#include <functional>',
                '#include "Utility/Range.h"',
            ]
            h_include_headers += other_headers

        header_content = '// This file is auto-generated by TAKSi v%s, DO NOT EDIT!\n\n#pragma once\n\n' % version.VER_STRING
        header_content += '\n'.join(h_include_headers) + '\n\n'

        if args.package is not None:
            header_content += '\nnamespace %s\n{\n\n' % args.package

        if self.load_gen is not None:
            header_content += self.load_gen.gen_global_class()

        for struct in descriptors:
            print(strutil.current_time(), 'start generate', struct['source'])
            header_content += self.gen_cpp_header(struct)

        if args.package is not None:
            header_content += '} // namespace %s\n' % args.package
        return header_content

    def run(self, descriptors, args):
        header_filepath = ''
        source_filepath = ''
        out_name = args.out_source_path
        if out_name is None:
            out_name = 'AutogenConfig'
        header_filepath = out_name + '.h'
        source_filepath = out_name + '.cpp'

        for struct in descriptors:
            genutil.setup_comment(struct)
            genutil.setup_key_value_mode(struct)

        cpp_content = ''
        header_content = self.gen_header_content(descriptors, args)
        if self.load_gen is not None:
            (array_delim, map_delims) = strutil.to_sep_delimiters(args.array_delim, args.map_delims)
            self.load_gen.init_delim(array_delim, map_delims)
            filename = os.path.split(out_name)[-1] + '.h'
            cpp_content = self.load_gen.gen_source_method(descriptors, args, filename)

        filename = os.path.abspath(header_filepath)
        strutil.save_content_if_not_same(filename, header_content, args.source_file_encoding)
        print('wrote C++ header file to', filename)

        if len(cpp_content) > 0:
            filename = os.path.abspath(source_filepath)
            modified = strutil.save_content_if_not_same(filename, cpp_content, args.source_file_encoding)
            if modified:
                print('wrote C++ source file to', filename)
            else:
                print('file content not modified', filename)
