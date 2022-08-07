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
import tabugen.generator.go.template as go_template


# 生成Go加载CSV文件数据代码
class GoCsvLoadGenerator:

    def __init__(self):
        self.TAB_SPACE = '\t'

    # 生成array类型的赋值代码
    def gen_array_field_assign(self, prefix: str, typename: str, name: str, valuetext: str, tabs: int) -> str:
        space = '\t' * tabs
        content = ''
        elem_type = types.array_element_type(typename)
        content += '%svar strArr = strings.Split(%s, "%s")\n' % (space, valuetext, predef.PredefDelim1)
        content += '%svar arr = make([]%s, 0, len(strArr))\n' % (space, elem_type)
        content += '%sfor _, s := range strArr {\n' % space
        expr = lang.map_go_parse_expr(elem_type, 's')
        content += '%s    var val = %s\n' % (space, expr)
        content += '%s    arr = append(arr, val)\n' % space
        content += '%s}\n' % space
        content += '%s%s%s = arr\n' % (space, prefix, name)
        return content

    # 生成map类型的赋值代码
    def gen_map_field_assign(self, prefix: str, typename: str, name: str, valuetext: str, tabs: int) -> str:
        space = '\t' * tabs
        key_type, val_type = types.map_key_value_types(typename)
        content = ''
        content += '%svar kvList = strings.Split(%s, "%s")\n' % (space, valuetext, predef.PredefDelim1)
        content += '%svar dict = make(map[%s]%s, len(kvList))\n' % (space, lang.map_go_type(key_type), lang.map_go_type(val_type))
        content += '%sfor _, kv := range kvList {\n' % space
        content += '%sif kv != "" {\n' % space
        content += '%s\tvar pair = strings.Split(kv, "%s")\n' % (space, predef.PredefDelim2)
        content += '%s\tvar key = %s\n' % (space, lang.map_go_parse_expr(key_type, 'pair[0]'))
        content += '%s\tvar val = %s\n' % (space, lang.map_go_parse_expr(val_type, 'pair[1]'))
        content += '%s\tdict[key] = val\n' % space
        content += '%s\t}\n' % space
        content += '%s}\n' % space
        content += '%s%s%s = dict\n' % (space, prefix, name)
        return content

    # 生成字段的赋值代码
    def gen_field_assign(self, prefix: str, origin_typename: str, name: str, valuetext: str, tabs: int) -> str:
        space = '\t' * tabs
        content = ''
        if origin_typename.startswith('array'):
            content += '%sif text := %s; text != "" {\n' % (space, valuetext)
            content += self.gen_array_field_assign(prefix, origin_typename, name, 'text', tabs + 1)
            content += '%s}\n' % space
        elif origin_typename.startswith('map'):
            content += '%sif text := %s; text != "" {\n' % (space, valuetext)
            content += self.gen_map_field_assign(prefix, origin_typename, name, 'text', tabs + 1)
            content += '%s}\n' % space
        elif origin_typename == 'string':
            content += '%s%s%s = strings.TrimSpace(%s)\n' % (space, prefix, name, valuetext)
        else:
            typename = lang.map_go_type(origin_typename)
            content += '%s%s%s = %s\n' % (space, prefix, name, lang.map_go_parse_expr(typename, valuetext))
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
        content = '%sfor i := 1; i < len(%s); i++ {\n' % (space, rec_name)
        content += '%s\tvar off = strconv.Itoa(i)\n' % space
        content += '%s\tvar val %s\n' % (space, inner_class_type)
        for i in range(step):
            field = struct['fields'][col + i]
            origin_typename = field['original_type_name']
            field_name = strutil.remove_suffix_number(field['camel_case_name'])
            text = '%s\tif str, found := %s["%s" + off]; found {\n' % (space, rec_name, field_name)
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

        keyidx = predef.PredefKeyColumn
        typeidx = predef.PredefValueTypeColumn

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
            if inner_start_col <= col < inner_end_col:
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
        filename = filepath + os.path.sep + 'helper.go'
        content = go_template.GO_HELP_FILE_HEAD_TEMPLATE % (ver, args.package)
        content += go_template.GO_HELP_FILE_TEMPLATE
        strutil.save_content_if_not_same(filename, content, 'utf-8')
