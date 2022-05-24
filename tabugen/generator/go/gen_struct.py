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

    def setup(self, name):
        if name is not None:
            if name == 'csv':
                self.load_gen = GoCsvLoadGenerator()

            else:
                print('content loader of name %s not implemented' % name)
                sys.exit(1)

    # 生成struct定义
    def gen_go_struct(self, struct, params):
        content = ''

        inner_class_done = False
        inner_typename = ''
        inner_var_name = ''
        inner_field_names, inner_fields = structutil.get_inner_class_mapped_fields(struct)
        if len(inner_fields) > 0:
            content += self.gen_go_inner_struct(struct, params.go_json_tag)
            inner_type_class = struct["options"][predef.PredefInnerTypeClass]
            inner_var_name = struct["options"][predef.PredefInnerTypeName]
            inner_typename = '[]%s' % inner_type_class

        vec_done = False
        vec_names, vec_name = structutil.get_vec_field_range(struct)
        fields = struct['fields']

        content += '// %s, %s\n' % (struct['comment'], struct['file'])
        content += 'type %s struct {\n' % struct['camel_case_name']
        for field in fields:
            if not field['enable']:
                continue
            text = ''
            field_name = field['name']
            if field_name in inner_field_names:
                if not inner_class_done:
                    if params.go_json_tag:
                        if self.json_snake_case:
                            inner_var_name = strutil.camel_to_snake(inner_var_name)
                        text += '    %s %s `json:"%s"` //\n' % (strutil.camel_case(inner_var_name),
                                                                inner_typename, inner_var_name)
                    else:
                        text += '    %s %s //\n' % (strutil.camel_case(inner_var_name), inner_typename)
                    inner_class_done = True
            else:
                typename = lang.map_go_type(field['original_type_name'])
                assert typename != "", field['original_type_name']

                if field_name not in vec_names:
                    if params.go_json_tag:
                        name = field['name']
                        if self.json_snake_case:
                            name = strutil.camel_to_snake(name)
                        text += '    %s %s `json:"%s"` // %s\n' % (field['camel_case_name'], typename,
                                                                   name, field['comment'])
                    else:
                        text += '    %s %s // %s\n' % (field['camel_case_name'], typename, field['comment'])
                elif not vec_done:
                    vec_done = True
                    if params.go_json_tag:
                        if self.json_snake_case:
                            vec_name = strutil.camel_to_snake(vec_name)
                        text += '    %s [%d]%s `json:"%s"` // %s\n' % (strutil.camel_case(vec_name), len(vec_names),
                                                                       typename, vec_name, field['comment'])
                    else:
                        text += '    %s [%d]%s // %s\n' % (vec_name, len(vec_names), typename, field['comment'])
            content += text

        return content

    # 内部class生成
    def gen_go_inner_struct(self, struct, go_json_tag):
        content = ''
        class_name = struct["options"][predef.PredefInnerTypeClass]
        inner_fields = structutil.get_inner_class_struct_fields(struct)
        content += 'type %s struct {\n' % class_name
        for field in inner_fields:
            typename = lang.map_go_type(field['original_type_name'])
            assert typename != "", field['original_type_name']
            if go_json_tag:
                name = field['name']
                if self.json_snake_case:
                    name = strutil.camel_to_snake(name)
                content += '    %s %s `json:"%s"` // %s\n' % (field['camel_case_name'], typename,
                                                              name, field['comment'])
            else:
                content += '    %s %s // %s\n' % (field['camel_case_name'], typename, field['comment'])
        content += '}\n\n'

        return content

    #
    def gen_struct_define(self, struct, params):
        content = ''
        content += self.gen_go_struct(struct, params)
        content += '}\n\n'
        return content

    def generate(self, struct, params):
        content = ''
        content += self.gen_struct_define(struct, params)
        if self.load_gen is not None:
            content += self.load_gen.gen_parse_method(struct)
            content += self.load_gen.gen_load_method(struct)
        return content

    def run(self, descriptors, filepath, args):
        content = ''
        content += go_template.GO_HEAD_TEMPLATE % (version.VER_STRING, args.package)

        if args.json_snake_case:
            self.json_snake_case = True

        if self.load_gen is not None:
            (array_delim, map_delims) = strutil.to_sep_delimiters(args.array_delim, args.map_delims)
            self.load_gen.setup(array_delim, map_delims)

        for struct in descriptors:
            content += self.generate(struct, args)

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


def unit_test():
    codegen = GoStructGenerator()
    codegen.setup('csv')


if __name__ == '__main__':
    unit_test()
