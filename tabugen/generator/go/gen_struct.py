"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import os
from argparse import Namespace
import tabugen.lang as lang
import tabugen.predef as predef
import tabugen.util.helper as helper
import tabugen.util.tableutil as tableutil
import tabugen.version as version
from tabugen.structs import Struct, StructField, ArrayField
from tabugen.generator.go.gen_csv_load import GoCsvLoadGenerator


# Go代码生成器
class GoStructGenerator:
    TAB_SPACE = '\t'

    @staticmethod
    def name():
        return "go"

    def __init__(self):
        self.parse_gen = None
        self.json_snake_case = False

    def enable_gen_parse(self, name):
        if name == 'csv':
            self.parse_gen = GoCsvLoadGenerator()

    # 生成字段定义
    def gen_field_define(self, field: StructField, max_type_len: int, max_name_len: int, json_snake_case: bool,
                         tabs: int) -> str:
        text = ''
        typename = lang.map_go_type(field.origin_type_name)
        assert typename != "", field.origin_type_name
        name = field.camel_case_name
        space = self.TAB_SPACE * tabs

        name = helper.pad_spaces(name, max_name_len + 4)
        typename = helper.pad_spaces(typename, max_type_len + 4)
        if json_snake_case:
            tag_name = field.name
            tag_name = helper.camel_to_snake(tag_name)
            text += '%s%s %s `json:"%s"`' % (space, name, typename, tag_name)
        else:
            text += '%s%s %s' % (space, name, typename)
        if field.comment:
            text += ' // %s' % field.comment
        text += '\n'
        return text

    def gen_array_define(self, field: ArrayField, max_type_len: int, max_name_len: int, json_snake_case: bool,
                         tabs: int) -> str:
        name = helper.camel_case(field.field_name)
        name = helper.pad_spaces(name, max_name_len + 4)
        typename = lang.map_go_type(field.type_name)
        typename = helper.pad_spaces(typename, max_type_len + 4)
        text = ''
        space = self.TAB_SPACE * tabs
        if json_snake_case:
            tag_name = field.field_name
            tag_name = helper.camel_to_snake(tag_name)
            text += '%s%s %s `json:"%s"`' % (space, name, typename, tag_name)
        else:
            text += '%s%s %s' % (space, name, typename)
        if field.comment:
            text += ' // %s' % field.comment
        text += '\n'
        return text

    def gen_kv_fields(self, struct: Struct, tabs: int, args: Namespace) -> str:
        space = self.TAB_SPACE * tabs
        key_idx = struct.get_column_index(predef.PredefKVKeyName)
        assert key_idx >= 0
        type_idx = struct.get_column_index(predef.PredefKVTypeName)
        comment_idx = struct.get_kv_comment_col()

        max_name_len, max_type_len = struct.get_kv_max_len(lang.map_go_type)
        content = 'type %s struct {\n' % struct.camel_case_name
        for row in struct.data_rows:
            key = row[key_idx]
            typename = 'int'
            if type_idx >= 0:
                typename = row[type_idx]
            if key == '' or typename == '':
                continue

            if args.legacy and typename.isdigit():
                typename = tableutil.legacy_kv_type(int(typename))

            typename = lang.map_go_type(typename)
            key_name = helper.pad_spaces(helper.camel_case(key), max_name_len + 4)
            typename = helper.pad_spaces(typename, max_type_len + 4)
            if args.json_snake_case:
                tag_name = helper.camel_to_snake(key)
                content += '%s%s %s `json:"%s"`' % (space, key_name, typename, tag_name)
            else:
                content += '%s%s %s' % (space, key_name, typename)
            if comment_idx >= 0:
                comment = row[comment_idx].strip()
                comment = comment.replace('\n', ' ')
                comment = comment.replace('//', '')
                if len(content) > 0:
                    content += '\t// %s' % comment
            content += '\n'
        content += '}\n'
        return content

    # 生成struct
    def gen_go_struct(self, struct: Struct, args: Namespace) -> str:
        content = ''

        if struct.comment:
            content += '// %s %s\n' % struct.comment

        if struct.options[predef.PredefParseKVMode]:
            return content + self.gen_kv_fields(struct, 1, args)

        content += 'type %s struct {\n' % struct.camel_case_name

        fields = struct.fields
        max_name_len = struct.max_field_name_length()
        max_type_len = struct.max_field_type_length(lang.map_go_type)

        for col, field in enumerate(fields):
            text = self.gen_field_define(field, max_type_len, max_name_len, args.json_snake_case, 1)
            content += text
        for array in struct.array_fields:
            content += self.gen_array_define(array, max_type_len, max_name_len, args.json_snake_case, 1)

        content += '}\n'
        return content

    def generate(self, struct: Struct, args: Namespace) -> str:
        content = ''
        content += self.gen_go_struct(struct, args)
        content += '\n'
        if self.parse_gen is not None:
            content += self.parse_gen.generate(struct)
        return content

    def run(self, descriptors: list[Struct], filepath: str, args: Namespace):
        content = '// This file is auto-generated by Tabugen v%s, DO NOT EDIT!\n\npackage %s\n\n'
        content = content % (version.VER_STRING, args.package)

        if args.json_snake_case:
            self.json_snake_case = True

        for struct in descriptors:
            content += self.generate(struct, args)

        if not filepath.endswith('.go'):
            filepath += '.go'
        filename = os.path.abspath(filepath)

        helper.save_content_if_not_same(filename, content, 'utf-8')
        print('wrote Go source to %s' % filename)

        if args.go_fmt:
            cmd = 'go fmt ' + filename
            goroot = os.getenv('GOROOT')
            if goroot is not None:
                cmd = goroot + '/bin/' + cmd
            print(cmd)
            os.system(cmd)
