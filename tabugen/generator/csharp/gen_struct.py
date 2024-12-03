# Copyright (C) 2018-present qi7chen@github. All rights reserved.
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
from tabugen.generator.csharp.gen_csv_load import CSharpCsvLoadGenerator


# C#代码生成器
class CSharpStructGenerator:
    TAB_SPACE = '    '

    @staticmethod
    def name():
        return "csharp"

    def __init__(self):
        self.load_gen = None

    def enable_gen_parse(self, name):
        if name is not None:
            if name == "csv":
                self.load_gen = CSharpCsvLoadGenerator()
            else:
                print('content loader of name %s not implemented' % name)
                sys.exit(1)

    # 生成字段类型定义
    def gen_field_define(self, field: StructField, max_type_len: int, max_name_len: int, json_snake_case: bool,  tabs: int) -> str:
        origin_type = field.origin_type_name
        typename = lang.map_cs_type(origin_type)
        if origin_type.startswith('array') or origin_type.startswith('map'):
            typename += '?'
        assert typename != "", field.origin_type_name
        if not json_snake_case:
            typename = helper.pad_spaces(typename, max_type_len + 1)
        name = lang.name_with_default_cs_value(field, typename, False)
        name = helper.pad_spaces(name, max_name_len + 8)
        space = self.TAB_SPACE * tabs
        text = '%spublic %s %s // %s\n' % (space, typename, name, field.comment)
        return text

    def gen_array_define(self, field: ArrayField, max_type_len: int, max_name_len: int, tabs: int) -> str:
        name = helper.camel_case(field.field_name)
        name = helper.pad_spaces(name + ';', max_name_len + 4)
        typename = lang.map_cs_type(field.type_name)
        typename = helper.pad_spaces(typename, max_type_len + 4)
        text = ''
        space = self.TAB_SPACE * tabs
        text += '%s%s %s' % (space, typename, name)
        if field.comment:
            text += ' // %s' % field.comment
        text += '\n'
        return text

    def gen_kv_fields(self, struct: Struct, args: Namespace) -> str:
        space = self.TAB_SPACE * 1
        key_idx = struct.get_column_index(predef.PredefKVKeyName)
        assert key_idx >= 0
        type_idx = struct.get_column_index(predef.PredefKVTypeName)
        comment_idx = struct.get_kv_comment_col()

        max_name_len, max_type_len = struct.get_kv_max_len(lang.map_cs_type)
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

            typename = lang.map_cs_type(typename)
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

    # 生成结构体定义
    def gen_struct(self, struct: Struct, args: Namespace):
        content = ''
        if struct.comment:
            content += '// %s, ' % struct.comment
        else:
            content += '// %s, ' % struct.name
        content += ' Created from %s\n' % struct.filepath

        if struct.options[predef.PredefParseKVMode]:
            return content + self.gen_kv_fields(struct, args)

        content += 'struct %s \n{\n' % struct.camel_case_name

        fields = struct.fields
        max_name_len = struct.max_field_name_length()
        max_type_len = struct.max_field_type_length(lang.map_cpp_type)

        for col, field in enumerate(fields):
            text = self.gen_field_define(field, max_type_len, max_name_len,  args.json_snake_case, 1)
            content += text
        for array in struct.array_fields:
            content += self.gen_array_define(array, max_type_len, max_name_len, 1)

        return content

    def generate(self, struct: Struct, args: Namespace):
        content = ''
        content += self.gen_struct(struct, args)
        if self.load_gen is not None:
            content += '\n'
            content += self.load_gen.generate(struct)
        content += '}\n'
        return content

    def run(self, descriptors: list[Struct], filepath: str, args: Namespace):
        content = '// This file is auto-generated by Tabugen v%s, DO NOT EDIT!\n\n' % version.VER_STRING
        content += 'using System;\n'
        content += 'using System.Collections.Generic;\n'
        if args.json_snake_case:
            content += 'using System.Text.Json.Serialization;\n'

        if args.package is not None:
            content += '\nnamespace %s\n{\n' % args.package

        for struct in descriptors:
            content += self.generate(struct, args)

        if args.package is not None:
            content += '\n} // namespace %s \n' % args.package

        if not filepath.endswith('.cs'):
            filepath += '.cs'
        filename = os.path.abspath(filepath)
        helper.save_content_if_not_same(filename, content, 'utf-8')
        print('wrote C# source file to', filename)
