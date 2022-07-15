"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import os

import tabugen.lang as lang
import tabugen.predef as predef
import tabugen.util.strutil as strutil
import tabugen.version as version
import tabugen.generator.go.template as go_template
from tabugen.generator.go.gen_csv_load import GoCsvLoadGenerator


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

    # Go代码生成器
    @staticmethod
    def gen_field_define(field, json_tag: bool, snake_case: bool, remove_suffix_num: bool) -> str:
        text = ''
        typename = lang.map_go_type(field['original_type_name'])
        assert typename != "", field['original_type_name']
        name = field['camel_case_name']
        if remove_suffix_num:
            name = strutil.remove_suffix_number(name)
        if json_tag:
            tag_name = field['name']
            if remove_suffix_num:
                tag_name = strutil.remove_suffix_number(tag_name)
            if snake_case:
                tag_name = strutil.camel_to_snake(tag_name)
            text += '    %s %s `json:"%s"` // %s\n' % (name, typename,
                                                       tag_name, field['comment'])
        else:
            text += '    %s %s // %s\n' % (name, typename, field['comment'])
        return text

    @staticmethod
    def gen_inner_field_define(struct, json_tag: bool, snake_case: bool) -> str:
        type_class_name = strutil.camel_case(struct["options"][predef.PredefInnerTypeClass])
        inner_field_name = struct["options"][predef.PredefInnerFieldName]
        assert len(inner_field_name) > 0
        if json_tag:
            tag_name = type_class_name
            if snake_case:
                tag_name = strutil.camel_to_snake(type_class_name)
            text = '\t%s []%s `json:"%s"` // \n' % (inner_field_name, type_class_name, tag_name)
        else:
            text = '\t%s []%s \n' % (inner_field_name, type_class_name)
        return text

    # 生成一个字段
    @staticmethod
    def gen_inner_type(struct, args):
        inner_fields = struct['inner_fields']
        start = inner_fields['start']
        step = inner_fields['step']
        type_class_name = strutil.camel_case(struct["options"][predef.PredefInnerTypeClass])
        assert len(type_class_name) > 0
        content = 'type %s struct {\n' % type_class_name
        col = start
        while col < start + step:
            field = struct['fields'][col]
            text = GoStructGenerator.gen_field_define(field, args.go_json_tag, args.json_snake_case, True)
            content += text
            col += 1
        content += '\n}\n'
        return content

    # 生成struct定义
    def gen_go_struct(self, struct, args):
        content = ''
        inner_start_col = -1
        inner_end_col = -1
        if 'inner_fields' in struct:
            inner_start_col = struct['inner_fields']['start']
            inner_end_col = struct['inner_fields']['end']
            content += self.gen_inner_type(struct, args)
            content += '\n'

        fields = struct['fields']
        inner_field_done = False
        content += '// %s %s\n' % (struct['comment'], struct['file'])
        content += 'type %s struct {\n' % struct['camel_case_name']
        for col, field in enumerate(fields):
            text = ''
            if inner_start_col <= col < inner_end_col:
                if not inner_field_done:
                    text = GoStructGenerator.gen_inner_field_define(struct, args.go_json_tag, args.json_snake_case)
                    inner_field_done = True
            else:
                text = GoStructGenerator.gen_field_define(field, args.go_json_tag, args.json_snake_case, False)
            content += text
        content += '\n}\n'
        return content

    def generate(self, struct, args):
        content = ''
        content += self.gen_go_struct(struct, args)
        content += '\n\n'
        if self.load_gen is not None:
            content += self.load_gen.gen_parse_method(struct)
            content += self.load_gen.gen_load_method(struct)
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
        if self.load_gen is not None:
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
