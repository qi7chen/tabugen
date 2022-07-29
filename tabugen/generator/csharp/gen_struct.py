# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import sys
import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.version as version
import tabugen.util.strutil as strutil
import tabugen.util.structutil as structutil
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

    def gen_field_define(self, field, max_name_len: int, max_type_len: int, remove_suffix_num: bool, tabs: int) -> str:
        typename = lang.map_cs_type(field['original_type_name'])
        assert typename != "", field['original_type_name']
        typename = strutil.pad_spaces(typename, max_type_len + 1)
        name = lang.name_with_default_cs_value(field, typename, remove_suffix_num)
        name = strutil.pad_spaces(name, max_name_len + 8)
        space = self.TAB_SPACE * tabs
        text = '%spublic %s %s // %s\n' % (space, typename.strip(), name, field['comment'])
        return text

    def gen_inner_type(self, struct) -> str:
        inner_fields = struct['inner_fields']
        start = inner_fields['start']
        step = inner_fields['step']
        type_class_name = strutil.camel_case(struct["options"][predef.PredefInnerTypeClass])
        assert len(type_class_name) > 0
        content = 'type %s struct {\n' % type_class_name
        col = start
        while col < start + step:
            field = struct['fields'][col]
            text = self.gen_field_define(field, True, 1)
            content += text
            col += 1
        content += '\n}\n'
        return content

    # 生成嵌套内部类定义
    def gen_inner_field(self, struct) -> str:
        content = ''
        class_name = struct["options"][predef.PredefInnerTypeClass]
        inner_fields = structutil.get_inner_class_struct_fields(struct)
        content += 'public class %s \n' % class_name
        content += '{\n'
        max_name_len = strutil.max_field_length(inner_fields, 'name', None)
        max_type_len = strutil.max_field_length(inner_fields, 'original_type_name', lang.map_cs_type)
        for field in inner_fields:
            typename = lang.map_cs_type(field['original_type_name'])
            assert typename != "", field['original_type_name']
            typename = strutil.pad_spaces(typename, max_type_len + 1)
            name = lang.name_with_default_cs_value(field, typename)
            name = strutil.pad_spaces(name, max_name_len + 8)
            content += '    public %s %s // %s\n' % (typename.strip(), name, field['comment'])
        content += '};\n\n'
        return content


    # 生成结构体定义
    def gen_cs_struct(self, struct):
        content = ''

        fields = struct['fields']
        if struct['options'][predef.PredefParseKVMode]:
            fields = structutil.get_struct_kv_fields(struct)

        inner_class_done = False
        inner_typename = ''
        inner_var_name = ''
        inner_field_names, inner_fields = structutil.get_inner_class_mapped_fields(struct)
        if len(inner_fields) > 0:
            content += self.gen_cs_inner_class(struct)
            inner_type_class = struct["options"][predef.PredefInnerTypeClass]
            inner_var_name = struct["options"][predef.PredefInnerTypeName]
            inner_typename = '%s[]' % inner_type_class

        content += '// %s, %s\n' % (struct['comment'], struct['file'])
        content += 'public class %s\n{\n' % struct['name']

        vec_done = False
        vec_names, vec_name = structutil.get_vec_field_range(struct)

        max_name_len = strutil.max_field_length(fields, 'name', None)
        max_type_len = strutil.max_field_length(fields, 'original_type_name', lang.map_cs_type)
        if len(inner_typename) > max_type_len:
            max_type_len = len(inner_typename)

        for field in fields:
            if not field['enable']:
                continue
            text = ''
            field_name = field['name']
            if field_name in inner_field_names:
                if not inner_class_done:
                    typename = strutil.pad_spaces(inner_typename, max_type_len)
                    text += '    public %s %s = null; \n' % (typename, inner_var_name)
                    inner_class_done = True
            else:
                typename = lang.map_cs_type(field['original_type_name'])
                assert typename != "", field['original_type_name']
                typename = strutil.pad_spaces(typename, max_type_len + 1)
                if field['name'] not in vec_names:
                    name = lang.name_with_default_cs_value(field, typename)
                    name = strutil.pad_spaces(name, max_name_len + 8)
                    text += '    public %s %s // %s\n' % (typename, name, field['comment'])
                elif not vec_done:
                    name = '%s = new %s[%d];' % (vec_name, typename.strip(), len(vec_names))
                    name = strutil.pad_spaces(name, max_name_len + 8)
                    text += '    public %s[] %s // %s\n' % (typename.strip(), name, field['comment'])
                    vec_done = True
            content += text
        return content





    def generate(self, struct, args):
        content = ''
        inner_start_col = -1
        inner_end_col = -1
        if 'inner_fields' in struct:
            inner_start_col = struct['inner_fields']['start']
            inner_end_col = struct['inner_fields']['end']
            content += self.gen_inner_type(struct)
            content += '\n'

        fields = struct['fields']
        inner_field_done = False
        content += '// %s %s\n' % (struct['comment'], struct['file'])
        content += 'type %s struct {\n' % struct['camel_case_name']
        for col, field in enumerate(fields):
            text = ''
            if inner_start_col <= col < inner_end_col:
                if not inner_field_done:
                    text = self.gen_inner_field_define(struct, args.go_json_tag, args.json_snake_case)
                    inner_field_done = True
            else:
                text = self.gen_field_define(field, args.go_json_tag, args.json_snake_case, False)
            content += text
        content += '\n}\n'
        return content

    def run(self, descriptors, filepath, args):
        content = '// This file is auto-generated by Tabugen v%s, DO NOT EDIT!\n\n' % version.VER_STRING
        content += 'using System;\n'
        content += 'using System.Collections.Generic;\n'

        if args.package is not None:
            content += '\nnamespace %s\n{\n' % args.package

        for struct in descriptors:
            content += self.generate(struct, args)

        if args.package is not None:
            content += '\n}\n'  # namespace

        filename = os.path.abspath(filepath)
        strutil.save_content_if_not_same(filename, content, 'utf-8')
        print('wrote C# source file to', filename)

