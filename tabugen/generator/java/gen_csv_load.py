# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.typedef as types
import tabugen.util.strutil as strutil


# java加载CSV代码生成器
class JavaCsvLoadGenerator:
    TAB_SPACE = '    '

    def __init__(self):
        pass

    def setup(self, name):
        pass

    # 生成array类型的赋值代码
    def gen_array_field_assign(self, prefix: str, typename: str, name: str, value_text: str, tabs: int) -> str:
        space = self.TAB_SPACE * tabs
        elem_type = types.array_element_type(typename)
        elem_java_type = lang.map_java_type(elem_type)
        # box_elem_type = lang.java_box_type(elem_java_type)
        content = ''
        content += '%sString[] strArr = StringUtils.split(%s, "%s");\n' % (space, value_text, predef.PredefDelim1)
        content += '%s%s%s = new %s[strArr.length];\n' % (space, prefix, name, elem_java_type)
        content += "%sfor(int i = 0; i < strArr.length; i++) \n" % space
        content += '%s{\n' % space
        expr = lang.map_java_parse_expr(elem_type, 'strArr[i]')
        content += '%s    %s%s[i] = %s;\n' % (space, prefix, name,  expr)
        content += '%s}\n' % space
        return content

    # 生成map赋值
    def gen_map_field_assign(self, prefix: str, typename: str, name: str, row_name: str, tabs: int) -> str:
        space = self.TAB_SPACE * tabs
        key_type, val_type = types.map_key_value_types(typename)
        box_key_type = lang.java_box_type(lang.map_java_type(key_type))
        box_val_type = lang.java_box_type(lang.map_java_type(val_type))

        content = '%sMap<%s, %s> mapVal = new HashMap<>();\n' % (space, box_key_type, box_val_type)
        content += '%sString[] kvList = StringUtils.split(%s, "%s");\n' % (space, row_name, predef.PredefDelim1)
        content += "%sfor(int i = 0; i < kvList.length; i++) \n" % space
        content += '%s{\n' % space
        content += '%s    String[] pair = kvList[i].split("%s");\n' % (space, predef.PredefDelim2)
        content += '%s    if (pair.length == 2) {\n' % space
        key_parse = lang.map_java_parse_expr(key_type, 'pair[0]')
        val_parse = lang.map_java_parse_expr(val_type, 'pair[1]')
        content += '%s        %s key = %s;\n' % (space, box_key_type, key_parse)
        content += '%s        %s val = %s;\n' % (space, box_val_type, val_parse)
        content += '%s        mapVal.put(key, val);\n' % space
        content += '%s    }\n' % space
        content += '%s}\n' % space
        content += '%s%s%s = mapVal;\n' % (space, prefix, name)
        return content

    # 字段比较
    def gen_field_assign(self, prefix: str, origin_typename: str, name: str, value_text: str, tabs: int) -> str:
        content = ''
        space = self.TAB_SPACE * tabs
        if origin_typename.startswith('array'):
            content += self.gen_array_field_assign(prefix, origin_typename, name, value_text, tabs)
        elif origin_typename.startswith('map'):
            content += self.gen_map_field_assign(prefix, origin_typename, name, value_text, tabs)
        elif origin_typename == 'string':
            content += '%s%s%s = StringUtils.strip(%s);\n' % (space, prefix, name, value_text)
        else:
            expr = lang.map_java_parse_expr(origin_typename, value_text)
            content += '%s%s%s = %s;\n' % (space, prefix, name, expr)
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
        content += '%s    ArrayList<%s> listVal = new ArrayList<>();\n' % (space, inner_class_type)
        content += '%s    for (int i = 1; i < %s.size(); i++)\n' % (space, rec_name)
        content += '%s    {\n' % space
        content += '%s        %s val = new %s();\n' % (space, inner_class_type, inner_class_type)
        content += '%s        String strVal = "";\n' % space
        for i in range(step):
            field = struct['fields'][col + i]
            origin_typename = field['original_type_name']
            field_name = strutil.remove_suffix_number(field['camel_case_name'])
            text = '%s        if ((strVal = %s.get("%s" + i)) != null) {\n' % (space, rec_name, field_name)
            text += self.gen_field_assign('val.', origin_typename, field_name, 'strVal', tabs+3)
            text += '%s        } else {\n' % space
            text += '%s            break; \n' % space
            text += '%s        }\n' % space
            content += text
        content += '%s        listVal.add(val);\n' % space
        content += '%s    }\n' % space
        content += '%s    if (!listVal.isEmpty()) {\n' % space
        content += '%s        %s%s = new %s[listVal.size()];\n' % (space, prefix, inner_var_name, inner_class_type)
        content += '%s        %s%s = listVal.toArray(%s%s);\n' % (space, prefix, inner_var_name, prefix, inner_var_name)
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
        content += '%s    String strTmp;\n' % space
        for col, field in enumerate(struct['fields']):
            if inner_start_col <= col < inner_end_col:
                if not inner_field_done:
                    content += self.gen_inner_fields_assign(struct, 'this.', 'record', tabs+1)
                    inner_field_done = True
            else:
                origin_typename = field['original_type_name']
                content += '%s    strTmp = record.get("%s");\n' % (space, field['name'])
                content += '%s    if (StringUtils.isNotEmpty(strTmp)) {\n' % space
                content += self.gen_field_assign('this.', origin_typename, field['name'], 'strTmp', tabs+2)
                content += '%s    }\n' % space

        content += '%s}\n\n' % space
        return content

    # 生成KV模式的Parse方法
    def gen_kv_parse_method(self, struct, tabs: int):
        keyidx = predef.PredefKeyColumn
        validx = predef.PredefValueColumn
        typeidx = predef.PredefValueTypeColumn
        assert keyidx >= 0 and validx >= 0 and typeidx >= 0

        rows = struct['data_rows']
        space = self.TAB_SPACE * tabs

        content = ''
        content += '%s// parse %s from string fields\n' % (space, struct['name'])
        content += '%spublic void parseFrom(Map<String, String> fields)\n' % space
        content += '%s{\n' % space
        content += '%s    String strTmp;\n' % space
        for row in rows:
            name = row[keyidx].strip()
            origin_typename = row[typeidx].strip()
            content += '%s    strTmp = fields.get("%s");\n' % (space, name)
            content += '%s    if (StringUtils.isNotEmpty(strTmp)) {\n' % space
            content += self.gen_field_assign('this.', origin_typename, name, 'strTmp', tabs + 2)
            content += '%s    }\n' % space
        content += '%s}\n\n' % space
        return content

    def generate(self, struct) -> str:
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct, 1)
        else:
            return self.gen_parse_method(struct, 1)
