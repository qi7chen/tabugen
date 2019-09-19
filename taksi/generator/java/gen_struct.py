# Copyright (C) 2018-present prototyped.cn. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import taksi.descriptor.predef as predef
import taksi.descriptor.lang as lang
import taksi.descriptor.strutil as strutil
import taksi.generator.genutil as genutil


# java结构生成器
class JavaStructGenerator:
    TAB_SPACE = '    '

    # 合并嵌套类
    def gen_java_inner_class(self, struct):
        content = ''
        class_name = struct["options"][predef.PredefInnerTypeClass]
        inner_fields = genutil.get_inner_class_struct_fields(struct)
        content += '    public static class %s \n' % class_name
        content += '    {\n'
        max_name_len = strutil.max_field_length(inner_fields, 'name', None)
        max_type_len = strutil.max_field_length(inner_fields, 'original_type_name', lang.map_java_type)
        for field in inner_fields:
            typename = lang.map_java_type(field['original_type_name'])
            assert typename != "", field['original_type_name']
            typename = strutil.pad_spaces(typename, max_type_len + 1)
            name = lang.name_with_default_java_value(field, typename)
            name = strutil.pad_spaces(name, max_name_len + 8)
            content += '        public %s %s // %s\n' % (typename.strip(), name, field['comment'])
        content += '    }\n\n'
        return content

    # 生成java类型
    def gen_java_class(self, struct):
        content = ''

        fields = struct['fields']
        if struct['options'][predef.PredefParseKVMode]:
            fields = genutil.get_struct_kv_fields(struct)

        content += '// %s, %s\n' % (struct['comment'], struct['file'])
        content += 'public class %s\n{\n' % struct['name']

        inner_class_done = False
        inner_typename = ''
        inner_var_name = ''
        inner_field_names, inner_fields = genutil.get_inner_class_mapped_fields(struct)
        if len(inner_fields) > 0:
            content += self.gen_java_inner_class(struct)
            inner_type_class = struct["options"][predef.PredefInnerTypeClass]
            inner_var_name = struct["options"][predef.PredefInnerTypeName]
            inner_typename = 'ArrayList<%s>' % inner_type_class

        vec_done = False
        vec_names, vec_name = genutil.get_vec_field_range(struct)

        max_name_len = strutil.max_field_length(fields, 'name', None)
        max_type_len = strutil.max_field_length(fields, 'original_type_name', lang.map_java_type)
        if len(inner_typename) > max_type_len:
            max_type_len = len(inner_typename)

        for field in fields:
            field_name = field['name']
            if field_name in inner_field_names:
                if not inner_class_done:
                    typename = strutil.pad_spaces(inner_typename, max_type_len)
                    content += '    public %s %s = new %s(); \n' % (typename, inner_var_name, typename)
                    inner_class_done = True
            else:
                typename = lang.map_java_type(field['original_type_name'])
                assert typename != "", field['original_type_name']
                typename = strutil.pad_spaces(typename, max_type_len + 1)
                if field['name'] not in vec_names:
                    name = lang.name_with_default_java_value(field, typename)
                    name = strutil.pad_spaces(name, max_name_len + 8)
                    content += '    public %s %s // %s\n' % (typename, name, field['comment'])
                elif not vec_done:
                    name = '%s = new %s[%d];' % (vec_name, typename.strip(), len(vec_names))
                    name = strutil.pad_spaces(name, max_name_len + 8)
                    content += '    public %s[] %s // %s\n' % (typename.strip(), name, field['comment'])
                    vec_done = True

        return content
