"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import os

import tabugen.lang as lang
import tabugen.predef as predef
import tabugen.typedef as types
import tabugen.util.strutil as strutil
import tabugen.util.tableutil as tableutil
import tabugen.generator.go.template as go_template


# 生成Go加载CSV文件数据代码
class GoCsvLoadGenerator:

    def __init__(self):
        self.TAB_SPACE = '\t'

    # 生成字段的赋值代码
    def gen_field_assign(self, prefix: str, origin_typename: str, name: str, valuetext: str, tabs: int) -> str:
        space = '\t' * tabs
        content = ''
        if types.is_array_type(origin_typename):
            elem_type = types.array_element_type(origin_typename)
            pfname = lang.map_go_parse_func(elem_type)
            content += '%s%s%s = parseArray(%s, %s)\n' % (space, prefix, name, valuetext, pfname)
        elif types.is_map_type(origin_typename):
            key_type, val_type = types.map_key_value_types(origin_typename)
            pfname1 = lang.map_go_parse_func(key_type)
            pfname2 = lang.map_go_parse_func(val_type)
            content += '%s%s%s = parseMap(%s, %s, %s)\n' % (space, prefix, name, valuetext, pfname1, pfname2)
        elif origin_typename == 'string':
            content += '%s%s%s = strings.TrimSpace(%s)\n' % (space, prefix, name, valuetext)
        else:
            typename = lang.map_go_type(origin_typename)
            pfname = lang.map_go_parse_func(typename)
            content += '%s%s%s = %s(%s)\n' % (space, prefix, name, pfname, valuetext)
        return content

    # 生成嵌入类型的字段加载代码
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
        content = '%sfor i := 0; i < len(%s); i++ {\n' % (space, rec_name)
        content += '%s\tvar val %s\n' % (space, inner_class_type)
        for i in range(step):
            field = struct['fields'][col + i]
            origin_typename = field['original_type_name']
            field_name = tableutil.remove_field_suffix(field['camel_case_name'])
            text = '%s\tif str, found := %s[fmt.Sprintf("%s[%%d]", i)]; found {\n' % (space, rec_name, field_name)
            text += self.gen_field_assign('val.', origin_typename, field_name, 'str', tabs + 2)
            text += '%s\t} else {\n ' % space
            text += '%s\t\tbreak\n' % space
            text += '%s\t}\n' % space
            content += text
        content += '%s\t%s%s = append(%s%s, val)\n' % (space, prefix, inner_var_name, prefix, inner_var_name)
        content += '%s}\n' % space
        return content

    # KV模式生成`ParseFrom`方法
    def gen_kv_parse_method(self, struct) -> str:
        content = ''
        rows = struct['data_rows']

        keyidx = struct['options']['key_column']
        typeidx = struct['options']['type_column']

        content += 'func (p *%s) ParseFrom(fields map[string]string) error {\n' % struct['camel_case_name']
        for row in rows:
            text = ''
            name = row[keyidx].strip()
            origin_typename = row[typeidx].strip()
            valuetext = 'fields["%s"]' % name
            content += self.gen_field_assign('p.', origin_typename, name, valuetext, 1)
            content += text
        content += '%sreturn nil\n' % '\t'
        content += '}\n\n'
        return content

    # 生成`ParseFrom`方法
    def gen_parse_method(self, struct) -> str:
        inner_start_col = -1
        inner_end_col = -1
        inner_field_done = False
        if 'inner_fields' in struct:
            inner_start_col = struct['inner_fields']['start']
            inner_end_col = struct['inner_fields']['end']

        content = ''
        content += 'func (p *%s) ParseFrom(record map[string]string) error {\n' % struct['camel_case_name']
        for col, field in enumerate(struct['fields']):
            if inner_start_col <= col <= inner_end_col:
                if not inner_field_done:
                    content += self.gen_inner_fields_assign(struct, 'p.', 'record', 1)
                    inner_field_done = True
            else:
                origin_typename = field['original_type_name']
                valuetext = 'record["%s"]' % field['name']
                content += self.gen_field_assign('p.', origin_typename, field['name'], valuetext, 1)

        content += '%sreturn nil\n' % '\t'
        content += '}\n'
        return content

    def generate(self, struct) -> str:
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct)
        else:
            return self.gen_parse_method(struct)

    # 生成helper.go文件
    def gen_helper_file(self, main_filepath: str, ver: str, args):
        filepath = os.path.abspath(os.path.dirname(main_filepath))
        filename = filepath + os.path.sep + 'conv.go'
        content = '// This file is auto-generated by Tabular, DO NOT EDIT!\npackage %s' % args.package
        content += go_template.GO_HELP_FILE_TEMPLATE
        strutil.save_content_if_not_same(filename, content, 'utf-8')
