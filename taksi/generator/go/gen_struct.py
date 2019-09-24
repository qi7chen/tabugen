# Copyright (C) 2018-present prototyped.cn. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


import taksi.descriptor.predef as predef
import taksi.descriptor.lang as lang
import taksi.generator.genutil as genutil
import taksi.descriptor.strutil as strutil


# Go struct generator
class GoStructGenerator():
    TAB_SPACE = '\t'

    #生成struct定义
    def gen_go_struct(self, struct, params):
        content = ''
        fields = struct['fields']
        if struct['options'][predef.PredefParseKVMode]:
            fields = genutil.get_struct_kv_fields(struct)

        json_decorate = params.get(predef.OptionJsonDecorate, False)

        inner_class_done = False
        inner_typename = ''
        inner_var_name = ''
        inner_field_names, inner_fields = genutil.get_inner_class_mapped_fields(struct)
        if len(inner_fields) > 0:
            content += self.gen_go_inner_struct(struct, json_decorate)
            inner_type_class = struct["options"][predef.PredefInnerTypeClass]
            inner_var_name = struct["options"][predef.PredefInnerTypeName]
            inner_typename = '[]%s' % inner_type_class

        vec_done = False
        vec_names, vec_name = genutil.get_vec_field_range(struct)

        content += '// %s, %s\n' % (struct['comment'], struct['file'])
        content += 'type %s struct\n{\n' % struct['camel_case_name']
        for field in fields:
            field_name = field['name']
            if field_name in inner_field_names:
                if not inner_class_done:
                    if json_decorate:
                        content += '    %s %s `json:"%s"` //\n' % (strutil.camel_case(inner_var_name),
                                                                   inner_typename, inner_var_name)
                    else:
                        content += '    %s %s //\n' % (strutil.camel_case(inner_var_name), inner_typename)
                    inner_class_done = True
            else:
                typename = lang.map_go_type(field['original_type_name'])
                assert typename != "", field['original_type_name']

                if field_name not in vec_names:
                    if json_decorate:
                        content += '    %s %s `json:"%s"` // %s\n' % (field['camel_case_name'], typename,
                                                                      field['comment'], field['name'])
                    else:
                        content += '    %s %s // %s\n' % (field['camel_case_name'], typename, field['comment'])
                elif not vec_done:
                    vec_done = True
                    if json_decorate:
                        content += '    %s [%d]%s `json:"%s"` // %s\n' % (strutil.camel_case(vec_name), len(vec_names),
                                                                          typename, field['comment'], vec_name)
                    else:
                        content += '    %s [%d]%s // %s\n' % (vec_name, len(vec_names), typename, field['comment'])

        return content

    # 内部class生成
    def gen_go_inner_struct(self, struct, json_decorate):
        content = ''
        class_name = struct["options"][predef.PredefInnerTypeClass]
        inner_fields = genutil.get_inner_class_struct_fields(struct)
        content += 'type %s struct {\n' % class_name
        for field in inner_fields:
            typename = lang.map_go_type(field['original_type_name'])
            assert typename != "", field['original_type_name']
            if json_decorate:
                content += '    %s %s `json:"%s"` // %s\n' % (field['camel_case_name'], typename,
                                                              field['comment'], field['name'])
            else:
                content += '    %s %s // %s\n' % (field['camel_case_name'], typename, field['comment'])
        content += '};\n\n'

        return content

    #
    def gen_struct_define(self, struct, params):
        content = ''
        content += self.gen_go_struct(struct, params)
        content += '}\n\n'
        return content
