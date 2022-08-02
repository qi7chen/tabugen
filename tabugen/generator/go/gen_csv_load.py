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
        pass

    # 生成array赋值
    def gen_array_field_assign(self, prefix: str, typename: str, name: str, valuetext: str, tabs: int) -> str:
        space = '\t' * tabs
        content = ''
        elem_type = types.array_element_type(typename)
        elem_type = lang.map_go_type(elem_type)

        content += '%svar strArr = strings.Split(%s, TABUGEN_SEP_DELIM1)\n' % (space, valuetext)
        content += '%svar arr = make([]%s, 0, len(strArr))\n' % (space, elem_type)
        content += '%sfor _, s := range strArr {\n' % space
        content += '%s    var val = %s(s)\n' % (space, lang.map_go_parse_fn(elem_type))
        content += '%s    arr = append(arr, val)\n' % space
        content += '%s}\n' % space
        content += '%s%s%s = arr\n' % (space, prefix, name)
        return content

    # 生成map赋值
    def gen_map_field_assign(self, prefix: str, typename: str, name: str, valuetext: str, tabs: int) -> str:
        space = '\t' * tabs
        k, v = types.map_key_value_types(typename)
        key_type = lang.map_go_type(k)
        val_type = lang.map_go_type(v)

        content = ''
        content += '%svar kvList = strings.Split(%s, TABUGEN_SEP_DELIM1)\n' % (space, valuetext)
        content += '%svar dict = make(map[%s]%s, len(kvList))\n' % (space, key_type, val_type)
        content += '%sfor _, kv := range kvList {\n' % space
        content += '%s    if kv != "" {\n' % space
        content += '%s    var pair = strings.Split(kv, TABUGEN_SEP_DELIM2)\n' % space
        content += '%s    var key = %s(pair[0])\n' % (space, lang.map_go_parse_fn(key_type))
        content += '%s    var val = %s(pair[1])\n' % (space, lang.map_go_parse_fn(val_type))
        content += '%s    dict[key] = val\n' % space
        content += '%s    }\n' % space
        content += '%s}\n' % space
        content += '%s%s%s = dict\n' % (space, prefix, name)
        return content

    # 生成赋值方法
    def gen_field_assign(self, prefix: str, origin_typename: str, name: str, valuetext: str, tabs: int) -> str:
        space = '\t' * tabs
        content = ''
        if origin_typename.startswith('array'):
            content += '\tif text := %s; text != "" {\n' % valuetext
            content += self.gen_array_field_assign(prefix, origin_typename, name, 'text', tabs)
            content += '\t}\n'
        elif origin_typename.startswith('map'):
            content += '\tif text := %s; text != "" {\n' % valuetext
            content += self.gen_map_field_assign(prefix, origin_typename, name, 'text', tabs)
            content += '\t}\n'
        elif origin_typename == 'string':
            content += '%s%s%s = strings.TrimSpace(%s)\n' % (space, prefix, name, valuetext)
        else:
            typename = lang.map_go_type(origin_typename)
            content += '%s%s%s = %s(%s)\n' % (space, prefix, name, lang.map_go_parse_fn(typename), valuetext)
        return content


    # 生成内部class的赋值方法
    def gen_inner_fields_assign(self, struct, prefix, rec_name):
        inner_fields = struct['inner_fields']
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerFieldName]
        assert len(inner_class_type) > 0 and len(inner_var_name) > 0

        start = inner_fields['start']
        end = inner_fields['end']
        step = inner_fields['step']
        assert start > 0 and end > 0 and step > 1

        col = start
        content = '\tfor i := 1; i < len(%s); i++ {\n' % rec_name
        content += '\t\tvar off = strconv.Itoa(i)\n'
        content += '\t\tvar val %s\n' % inner_class_type
        for i in range(step):
            field = struct['fields'][col + i]
            origin_typename = field['original_type_name']
            field_name = strutil.remove_suffix_number(field['camel_case_name'])
            valuetext = '%s["%s" + off]' % (rec_name, field_name)
            text = 'if str, found := %s["%s" + off]; found {\n' % (rec_name, field_name)
            text += self.gen_field_assign('val.', origin_typename, field_name, 'str', 2)
            text += '} else {\n \tbreak \n }\n'
            content += text
        content += '%s%s = append(%s%s, val)\n' % (prefix, inner_var_name, prefix, inner_var_name)
        content += '\t}\n'
        return content

    # KV模式的ParseFromRow方法
    def gen_kv_parse_method(self, struct):
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
            content += self.gen_field_assign('p.', origin_typename, name, valuetext, 2)
            content += text
        content += '%sreturn nil\n' % '\t'
        content += '}\n\n'
        return content

    # 生成ParseFromRow方法
    def gen_parse_method(self, struct):
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
                    content += self.gen_inner_fields_assign(struct, 'p.', 'record')
                    inner_field_done = True
            else:
                origin_typename = field['original_type_name']
                valuetext = 'record["%s"]' % field['name']
                content += self.gen_field_assign('p.', origin_typename, field['name'], valuetext, 2)

        content += '%sreturn nil\n' % '\t'
        content += '}\n\n'
        return content


    # 生成Load方法
    def generate(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct)
        else:
            return self.gen_parse_method(struct)

    # 生成helper.go文件
    def gen_helper_file(self, main_filepath, ver, args):
        const_def = go_template.GO_CONST_TEMPLATE % (predef.PredefDelim1, predef.PredefDelim2)
        filepath = os.path.abspath(os.path.dirname(main_filepath))
        filename = filepath + os.path.sep + 'helper.go'
        content = go_template.GO_HELP_FILE_HEAD_TEMPLATE % (ver, args.package)
        content += go_template.GO_HELP_FILE_TEMPLATE + const_def
        strutil.save_content_if_not_same(filename, content, 'utf-8')
