# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.typedef as types
import tabugen.util.tableutil as tableutil


# java加载CSV代码生成器
class JavaCsvLoadGenerator:
    TAB_SPACE = '    '

    def __init__(self):
        pass

    def setup(self, name):
        pass

    # 字段比较
    def gen_field_assign(self, prefix: str, origin_typename: str, name: str, value_text: str, tabs: int) -> str:
        content = ''
        space = self.TAB_SPACE * tabs
        if types.is_array_type(origin_typename):
            elem_type = types.array_element_type(origin_typename)
            elem_java_type = lang.map_java_type(elem_type)
            print('elem_java_type', elem_java_type)
            func_name = lang.map_java_parse_array_func(elem_java_type)
            content += '%s%s%s = %s(%s);\n' % (space, prefix, name, func_name, value_text)
        elif types.is_map_type(origin_typename):
            key_type, val_type = types.map_key_value_types(origin_typename)
            box_key_type = lang.java_box_type(lang.map_java_type(key_type))
            box_val_type = lang.java_box_type(lang.map_java_type(val_type))
            content += '%s%s%s = Conv.parseMap(%s, %s.class, %s.class);\n' % (space, prefix, name, value_text, box_key_type, box_val_type)
        elif origin_typename == 'string':
            content += '%s%s%s = %s;\n' % (space, prefix, name, value_text)
        else:
            func_name = lang.map_java_parse_func(origin_typename)
            content += '%s%s%s = %s(%s);\n' % (space, prefix, name, func_name, value_text)
        return content

    # 生成内部类的parse
    def gen_inner_fields_assign(self, struct, prefix: str, rec_name: str, tabs: int) -> str:
        inner_fields = struct['inner_fields']
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerFieldName]
        assert len(inner_class_type) > 0 and len(inner_var_name) > 0

        start = inner_fields['start']
        end = inner_fields['end']
        step = inner_fields['step']
        assert start > 0 and end > 0 and step > 1

        space = self.TAB_SPACE * tabs
        col = start
        content = '%s{\n' % space
        content += '%s    ArrayList<%s> list = new ArrayList<>();\n' % (space, inner_class_type)
        content += '%s    for (int i = 0; i < %s.size(); i++)\n' % (space, rec_name)
        content += '%s    {\n' % space
        content += '%s        %s val = new %s();\n' % (space, inner_class_type, inner_class_type)
        content += '%s        String strVal = "";\n' % space
        for i in range(step):
            field = struct['fields'][col + i]
            origin_typename = field['original_type_name']
            field_name = tableutil.remove_field_suffix(field['camel_case_name'])
            text = '%s        if ((strVal = %s.get(String.format("%s[%%d]", i))) != null) {\n' % (space, rec_name, field_name)
            text += self.gen_field_assign('val.', origin_typename, field_name, 'strVal', tabs+3)
            if i == 0:
                text += '%s        } else {\n' % space
                text += '%s            break; \n' % space
                text += '%s        }\n' % space
            else:
                text += '%s        } \n' % space
            content += text
        content += '%s        list.add(val);\n' % space
        content += '%s    }\n' % space
        content += '%s    if (!list.isEmpty()) {\n' % space
        content += '%s        %s%s = new %s[list.size()];\n' % (space, prefix, inner_var_name, inner_class_type)
        content += '%s        %s%s = list.toArray(%s%s);\n' % (space, prefix, inner_var_name, prefix, inner_var_name)
        content += '%s    }\n' % space
        content += '%s}\n' % space
        return content

    # 生成ParseFrom方法
    def gen_parse_method(self, struct, tabs: int):
        inner_start_col = -1
        inner_end_col = -1
        inner_field_done = False
        if 'inner_fields' in struct:
            inner_start_col = struct['inner_fields']['start']
            inner_end_col = struct['inner_fields']['end']

        space = self.TAB_SPACE * tabs
        content = ''
        content += '%spublic void parseFrom(Map<String, String> record) \n' % space
        content += '%s{\n' % space
        for col, field in enumerate(struct['fields']):
            if inner_start_col <= col <= inner_end_col:
                if not inner_field_done:
                    content += self.gen_inner_fields_assign(struct, 'this.', 'record', tabs+1)
                    inner_field_done = True
            else:
                origin_typename = field['original_type_name']
                key = 'record.get("%s")' % field['name']
                content += self.gen_field_assign('this.', origin_typename, field['name'], key, tabs+1)

        content += '%s}\n\n' % space
        return content

    # 生成KV模式的Parse方法
    def gen_kv_parse_method(self, struct, tabs: int):
        keyidx = struct['options']['key_column']
        validx = struct['options']['value_column']
        typeidx = struct['options']['type_column']
        assert keyidx >= 0 and validx >= 0 and typeidx >= 0

        rows = struct['data_rows']
        space = self.TAB_SPACE * tabs

        content = ''
        content += '%s// parse %s from string fields\n' % (space, struct['name'])
        content += '%spublic void parseFrom(Map<String, String> fields)\n' % space
        content += '%s{\n' % space
        for row in rows:
            name = row[keyidx].strip()
            origin_typename = row[typeidx].strip()
            key = 'fields.get("%s")' % name
            content += self.gen_field_assign('this.', origin_typename, name, key, tabs + 1)
        content += '%s}\n\n' % space
        return content

    def generate(self, struct) -> str:
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct, 1)
        else:
            return self.gen_parse_method(struct, 1)
