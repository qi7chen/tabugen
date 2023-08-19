"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import os

import tabugen.lang as lang
import tabugen.predef as predef
import tabugen.util.strutil as strutil
import tabugen.util.tableutil as tableutil
import tabugen.version as version
import tabugen.generator.go.template as go_template
from tabugen.generator.go.gen_csv_load import GoCsvLoadGenerator


# Go代码生成器
class GoStructGenerator:
    TAB_SPACE = '\t'

    @staticmethod
    def name():
        return "go"

    def __init__(self):
        self.load_gen = None
        self.json_snake_case = False

    def enable_gen_parse(self, name):
        if name == 'csv':
            self.load_gen = GoCsvLoadGenerator()

    # 生成字段定义
    def gen_field_define(self, field, max_type_len: int, max_name_len: int, json_snake_case: bool, remove_suffix_num: bool, tabs: int) -> str:
        text = ''
        typename = lang.map_go_type(field['original_type_name'])
        assert typename != "", field['original_type_name']
        name = field['camel_case_name']
        space = self.TAB_SPACE * tabs
        if remove_suffix_num:
            name = tableutil.remove_field_suffix(name)

        name = strutil.pad_spaces(name, max_name_len + 4)
        typename = strutil.pad_spaces(typename, max_type_len + 4)
        if json_snake_case:
            tag_name = field['name']
            if remove_suffix_num:
                tag_name = tableutil.remove_field_suffix(tag_name)
            tag_name = strutil.camel_to_snake(tag_name)
            text += '%s%s %s `json:"%s"` // %s\n' % (space, name, typename, tag_name, field['comment'])
        else:
            text += '%s%s %s // %s\n' % (space, name, typename, field['comment'])
        return text

    # 生成嵌入类型的字段定义
    def gen_inner_fields(self, struct, max_type_len: int, max_name_len: int, json_snake_case: bool, tabs: int) -> str:
        type_class_name = strutil.camel_case(struct["options"][predef.PredefInnerTypeClass])
        inner_field_name = struct["options"][predef.PredefInnerFieldName]
        assert len(inner_field_name) > 0
        space = self.TAB_SPACE * tabs
        type_class_name = strutil.pad_spaces(type_class_name, max_type_len + 4)
        inner_field_name = strutil.pad_spaces(inner_field_name, max_name_len + 4)
        if json_snake_case:
            tag_name = strutil.camel_to_snake(type_class_name)
            text = '%s%s []%s `json:"%s"` // \n' % (space, inner_field_name, type_class_name, tag_name)
        else:
            text = '%s%s []%s \n' % (space, inner_field_name, type_class_name)
        return text

    # 生成嵌入类型定义
    def gen_inner_type(self, struct, args) -> str:
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

        content = 'type %s struct {\n' % type_class_name
        col = start
        while col < start + step:
            field = struct['fields'][col]
            text = self.gen_field_define(field, max_type_len, max_name_len, args.json_snake_case, True, 1)
            content += text
            col += 1
        content += '}\n'
        return content

    # 生成struct
    def gen_go_struct(self, struct, args) -> str:
        content = ''

        inner_start_col = -1
        inner_end_col = -1
        inner_field_done = False
        if 'inner_fields' in struct:
            inner_start_col = struct['inner_fields']['start']
            inner_end_col = struct['inner_fields']['end']
            content += self.gen_inner_type(struct, args)
            content += '\n'

        content += '// %s %s\n' % (struct['comment'], struct['file'])
        content += 'type %s struct {\n' % struct['camel_case_name']

        fields = struct['fields']
        max_name_len = strutil.max_field_length(fields, 'name', None)
        max_type_len = strutil.max_field_length(fields, 'original_type_name', lang.map_go_type)

        for col, field in enumerate(fields):
            text = ''
            if inner_start_col <= col <= inner_end_col:
                if not inner_field_done:
                    text = self.gen_inner_fields(struct, max_type_len, max_name_len,  args.json_snake_case, 1)
                    inner_field_done = True
            else:
                text = self.gen_field_define(field, max_type_len, max_name_len, args.json_snake_case, False, 1)
            content += text
        content += '}\n'
        return content

    def generate(self, struct, args) -> str:
        content = ''
        content += self.gen_go_struct(struct, args)
        content += '\n'
        if self.load_gen is not None:
            content += self.load_gen.generate(struct)
        return content

    def run(self, descriptors, filepath, args):
        content = ''
        content += go_template.GO_HEAD_TEMPLATE % (version.VER_STRING, args.package)

        if args.json_snake_case:
            self.json_snake_case = True

        for struct in descriptors:
            content += self.generate(struct, args)

        if not filepath.endswith('.go'):
            filepath += '.go'
        filename = os.path.abspath(filepath)
        if self.load_gen is not None and args.with_conv:
            self.load_gen.gen_helper_file(filename, version.VER_STRING, args)

        strutil.save_content_if_not_same(filename, content, 'utf-8')
        print('wrote Go source to %s' % filename)

        if args.go_fmt:
            cmd = 'go fmt ' + filename
            goroot = os.getenv('GOROOT')
            if goroot is not None:
                cmd = goroot + '/bin/' + cmd
            print(cmd)
            os.system(cmd)
