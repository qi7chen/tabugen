# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import sys
import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.version as version
import tabugen.util.strutil as strutil
import tabugen.generator.csharp.template as cs_template
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
    def gen_field_define(self, field, max_type_len: int, max_name_len: int, json_snake_case: bool,  tabs: int) -> str:
        origin_type = field['original_type_name']
        typename = lang.map_cs_type(origin_type)
        if origin_type.startswith('array') or origin_type.startswith('map'):
            typename += '?'
        assert typename != "", field['original_type_name']
        if not json_snake_case:
            typename = strutil.pad_spaces(typename, max_type_len + 1)
        name = lang.name_with_default_cs_value(field, typename, False)
        name = strutil.pad_spaces(name, max_name_len + 8)
        space = self.TAB_SPACE * tabs
        text = '%spublic %s %s // %s\n' % (space, typename, name, field['comment'])
        return text

    # 生成嵌入类型的字段定义
    def gen_inner_field_define(self, struct, max_type_len: int, max_name_len: int, json_snake_case: bool, tabs: int) -> str:
        type_class_name = strutil.camel_case(struct["options"][predef.PredefInnerTypeClass])
        inner_field_name = struct["options"][predef.PredefInnerFieldName]
        type_name = '%s[]' % type_class_name
        type_name = strutil.pad_spaces(type_name, max_type_len + 1)
        inner_field_name = strutil.pad_spaces(inner_field_name, max_name_len + 1)
        assert len(inner_field_name) > 0
        space = self.TAB_SPACE * tabs
        text = '%spublic %s %s { get; set; } \n' % (space, type_name, inner_field_name)
        return text

    # 生成嵌入类型
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
            type_len = len(lang.map_cs_type(field['original_type_name']))
            if name_len > max_name_len:
                max_name_len = name_len
            if type_len > max_type_len:
                max_type_len = type_len

        space = self.TAB_SPACE * tabs
        content = '%spublic struct %s \n' % (space, type_class_name)
        content += '%s{\n' % space
        col = start
        space2 = self.TAB_SPACE * (tabs + 1)
        while col < start + step:
            field = struct['fields'][col]
            typename = lang.map_cs_type(field['original_type_name'])
            assert typename != "", field['original_type_name']
            typename = strutil.pad_spaces(typename, max_type_len + 1)
            name = lang.name_with_default_cs_value(field, typename, True)
            name = strutil.pad_spaces(name, max_name_len + 8)
            content += '%spublic %s %s // %s\n' % (space2, typename, name, field['comment'])
            col += 1

        # content += '\n%s    // default constructor\n' % space
        # content += '%s    public %s() { \n' % (space, type_class_name)
        # content += '%s    }\n' % space

        content += '%s}\n' % space
        return content

    # 生成结构体定义
    def gen_struct(self, struct, args):
        content = '// %s %s\n' % (struct['comment'], struct['file'])
        content += 'public struct %s \n' % struct['camel_case_name']
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
        max_type_len = strutil.max_field_length(fields, 'original_type_name', lang.map_cs_type)
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

        # content += '\n    // default constructor\n'
        # content += '    public %s() { \n' % struct['camel_case_name']
        # content += '    }\n'

        # 这里留着后续生成 `}`
        return content

    def generate(self, struct, args):
        content = ''
        content += self.gen_struct(struct, args)
        if self.load_gen is not None:
            content += '\n'
            content += self.load_gen.generate(struct)
        content += '}\n'
        return content

    def run(self, descriptors, filepath: str, args):
        content = '// This file is auto-generated by Tabugen v%s, DO NOT EDIT!\n\n' % version.VER_STRING
        content += 'using System;\n'
        content += 'using System.Collections.Generic;\n'
        if args.json_snake_case:
            content += 'using System.Text.Json.Serialization;\n'

        util_content = '// This file is auto-generated by Tabugen, DO NOT EDIT!\n\n'

        if args.package is not None:
            content += '\nnamespace %s\n{\n' % args.package
            util_content += '\nnamespace %s\n{\n' % args.package

        for struct in descriptors:
            content += self.generate(struct, args)

        util_content += cs_template.CS_CONV_TEMPLATE

        if args.package is not None:
            content += '\n} // namespace %s \n' % args.package
            util_content += '\n} // namespace %s \n' % args.package

        if not filepath.endswith('.cs'):
            filepath += '.cs'
        filename = os.path.abspath(filepath)
        strutil.save_content_if_not_same(filename, content, 'utf-8')
        print('wrote C# source file to', filename)

        if args.with_conv and self.load_gen is not None:
            filename = os.path.join(os.path.split(filepath)[0], 'Conv.cs')
            strutil.save_content_if_not_same(filename, util_content, 'utf-8')
            print('wrote C# source file to', filename)
