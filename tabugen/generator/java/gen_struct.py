# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import sys
import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.version as version
import tabugen.util.strutil as strutil
import tabugen.generator.java.template as java_template
from tabugen.generator.java.gen_csv_load import JavaCsvLoadGenerator


# java代码生成器
class JavaStructGenerator:
    TAB_SPACE = '    '

    @staticmethod
    def name():
        return "java"

    def __init__(self):
        self.load_gen = None

    def enable_gen_parse(self, name):
        if name is not None:
            if name == 'csv':
                self.load_gen = JavaCsvLoadGenerator()
            else:
                print('content loader of name %s not implemented' % name)
                sys.exit(1)

    def gen_field_define(self, field, max_type_len: int, max_name_len: int, json_snake_case: bool,  tabs: int) -> str:
        origin_type = field['original_type_name']
        typename = lang.map_java_type(origin_type)
        assert typename != "", field['original_type_name']
        if not json_snake_case:
            typename = strutil.pad_spaces(typename, max_type_len + 1)
        name = lang.name_with_default_java_value(field, typename, False)
        name = strutil.pad_spaces(name, max_name_len + 8)
        space = self.TAB_SPACE * tabs
        text = '%spublic %s %s // %s\n' % (space, typename, name, field['comment'])
        return text

    def gen_inner_field_define(self, struct, max_type_len: int, max_name_len: int, json_snake_case: bool, tabs: int) -> str:
        type_class_name = strutil.camel_case(struct["options"][predef.PredefInnerTypeClass])
        inner_field_name = struct["options"][predef.PredefInnerFieldName]
        type_name = '%s[]' % type_class_name
        type_name = strutil.pad_spaces(type_name, max_type_len + 1)
        inner_field_name = strutil.pad_spaces(inner_field_name, max_name_len + 1)
        assert len(inner_field_name) > 0
        space = self.TAB_SPACE * tabs
        text = '%spublic %s %s; \n' % (space, type_name, inner_field_name)
        return text

    def gen_inner_type(self, struct, tabs: int) -> str:
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
            type_len = len(lang.map_java_type(field['original_type_name']))
            if name_len > max_name_len:
                max_name_len = name_len
            if type_len > max_type_len:
                max_type_len = type_len

        space = self.TAB_SPACE * tabs
        content = '%spublic static class %s \n' % (space, type_class_name)
        content += '%s{\n' % space
        col = start
        space2 = self.TAB_SPACE * (tabs + 1)
        while col < start + step:
            field = struct['fields'][col]
            typename = lang.map_java_type(field['original_type_name'])
            assert typename != "", field['original_type_name']
            typename = strutil.pad_spaces(typename, max_type_len + 1)
            name = lang.name_with_default_java_value(field, typename, True)
            name = strutil.pad_spaces(name, max_name_len + 8)
            content += '%spublic %s %s // %s\n' % (space2, typename, name, field['comment'])
            col += 1
        content += '%s}\n' % space
        return content

    def gen_class(self, struct, args) -> str:
        content = '// %s %s\n' % (struct['comment'], struct['file'])
        content += 'public class %s \n' % struct['camel_case_name']
        content += '{\n'

        inner_start_col = -1
        inner_end_col = -1
        inner_field_done = False
        if 'inner_fields' in struct:
            inner_start_col = struct['inner_fields']['start']
            inner_end_col = struct['inner_fields']['end']
            content += self.gen_inner_type(struct, 1)
            content += '\n'

        fields = struct['fields']
        max_name_len = strutil.max_field_length(fields, 'name', None)
        max_type_len = strutil.max_field_length(fields, 'original_type_name', lang.map_java_type)
        if inner_start_col >= 0:
            type_class_name = strutil.camel_case(struct["options"][predef.PredefInnerTypeClass])
            field_name = '%s[]' % type_class_name
            if len(field_name) > max_type_len:
                max_type_len = len(field_name)

        for col, field in enumerate(fields):
            text = ''
            if inner_start_col <= col <= inner_end_col:
                if not inner_field_done:
                    text = self.gen_inner_field_define(struct, max_type_len, max_name_len, args.json_snake_case, 1)
                    inner_field_done = True
            else:
                text = self.gen_field_define(field, max_type_len, max_name_len, args.json_snake_case, 1)
            content += text
        return content

    # 生成对象及方法
    def generate(self, struct, args) -> str:
        content = '\n'
        content += self.gen_class(struct, args)
        if self.load_gen is not None:
            content += '\n'
            content += self.load_gen.generate(struct)
        content += '}\n'
        return content

    # 生成代码
    def run(self, descriptors, filepath, args):
        mgr_content = '// This file is auto-generated by taxi v%s, DO NOT EDIT!\n\n' % version.VER_STRING

        try:
            os.mkdir(filepath)
        except OSError as e:
            pass

        if args.package is not None:
            pkgname = args.package
            names = [filepath] + pkgname.split('.')
            basedir = '/'.join(names)
            filepath = basedir
            mgr_content += 'package %s;' % pkgname
            try:
                print('make dir', basedir)
                os.makedirs(basedir)
            except OSError as e:
                pass

        class_dict = {}

        pkg_imports = [
            'import java.util.*;',
        ]

        for struct in descriptors:
            content = '// This file is auto-generated by Tabugen v%s, DO NOT EDIT!\n\n' % version.VER_STRING
            filename = '%s.java' % struct['camel_case_name']
            # print(filename)
            if args.package:
                filename = '%s/%s' % (filepath, filename)
                content += 'package %s;\n\n' % args.package
            content += '\n'.join(pkg_imports)
            content += '\n'
            content += self.generate(struct, args)
            class_dict[filename] = content

        mgr_content += '}\n'

        if self.load_gen is not None and args.with_conv:
            filename = '%s/%s' % (filepath, 'Conv.java')
            util_content = java_template.JAVA_CONV_TEMPLATE % args.package
            class_dict[filename] = util_content

        for filename in class_dict:
            content = class_dict[filename]
            filename = os.path.abspath(filename)
            strutil.save_content_if_not_same(filename, content, args.source_file_encoding)
            print('wrote Java source file to', filename)


