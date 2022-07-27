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

    # 生成赋值方法
    @staticmethod
    def gen_field_assign_stmt(name, typename, valuetext, tabs, tips):
        content = ''
        space = '\t' * tabs
        if typename == 'string':
            return '%s%s = %s\n' % (space, name, valuetext)
        else:
            content += '%s%s = %s(%s)\n' % (space, name, lang.map_go_parse_fn(typename), valuetext)
        return content

    # 生成array赋值
    @staticmethod
    def gen_field_array_assign_stmt(prefix, typename, name, row_name, tabs):
        space = '\t' * tabs
        content = ''
        elem_type = types.array_element_type(typename)
        elem_type = lang.map_go_type(elem_type)

        content += '%svar strArr = strings.Split(%s, TABUGEN_SEP_DELIM1)\n' % (space, row_name)
        content += '%svar arr = make([]%s, 0, len(strArr))\n' % (space, elem_type)
        content += '%sfor _, s := range strArr {\n' % space
        content += '%s    var val = %s(s)\n' % (space, lang.map_go_parse_fn(elem_type))
        content += '%s    arr = append(arr, val)\n' % space
        content += '%s}\n' % space
        content += '%s%s%s = arr\n' % (space, prefix, name)
        return content

    # 生成map赋值
    @staticmethod
    def gen_field_map_assign_stmt(prefix, typename, name, row_name, tabs):
        space = '\t' * tabs
        k, v = types.map_key_value_types(typename)
        key_type = lang.map_go_type(k)
        val_type = lang.map_go_type(v)

        content = ''
        content += '%svar kvList = strings.Split(%s, TABUGEN_SEP_DELIM1)\n' % (space, row_name)
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

    # KV模式的ParseFromRow方法
    @staticmethod
    def gen_kv_parse_method(struct):
        content = ''
        rows = struct['data_rows']

        keyidx = predef.PredefKeyColumn
        validx = predef.PredefValueColumn
        typeidx = predef.PredefValueTypeColumn

        content += 'func (p *%s) ParseFields(fields map[string]string) error {\n' % struct['camel_case_name']

        idx = 0
        for row in rows:
            text = ''
            name = row[keyidx].strip()
            origin_typename = row[typeidx].strip()
            typename = lang.map_go_type(origin_typename)
            valuetext = 'text'
            # print('kv', name, origin_typename, valuetext)
            if origin_typename.startswith('array'):
                text += '\tif text := fields["%s"]; text != "" {\n' % name
                text += GoCsvLoadGenerator.gen_field_array_assign_stmt('p.', origin_typename, name, valuetext, 2)
                text += '%s}\n' % '\t'
            elif origin_typename.startswith('map'):
                text += '\tif text := fields["%s"]; text != "" {\n' % name
                text += GoCsvLoadGenerator.gen_field_map_assign_stmt('p.', origin_typename, name, valuetext, 2)
                text += '%s}\n' % '\t'
            else:
                valuetext = 'fields["%s"]' % name
                content += GoCsvLoadGenerator.gen_field_assign_stmt('p.' + name, typename, valuetext, 2, idx)
            content += text
        content += '%sreturn nil\n' % '\t'
        content += '}\n\n'
        return content

    # 生成ParseFromRow方法
    @staticmethod
    def gen_parse_method(struct):
        if struct['options'][predef.PredefParseKVMode]:
            return GoCsvLoadGenerator.gen_kv_parse_method(struct)

        inner_start_col = -1
        inner_end_col = -1
        inner_field_done = False
        if 'inner_fields' in struct:
            inner_start_col = struct['inner_fields']['start']
            inner_end_col = struct['inner_fields']['end']

        content = ''
        content += 'func (p *%s) ParseFrom(record map[string]string) error {\n' % struct['camel_case_name']

        idx = 0
        prefix = 'p.'
        for field in struct['fields']:
            col = field['column_index']
            text = ''
            if inner_start_col <= col < inner_end_col:
                if not inner_field_done:
                    text = GoCsvLoadGenerator.gen_inner_class_parse(struct, prefix, 'record')
                    inner_field_done = True
            else:
                fname = field['name']
                origin_type_name = field['original_type_name']
                typename = lang.map_go_type(origin_type_name)
                field_name = field['camel_case_name']
                valuetext = 'text'
                if origin_type_name.startswith('array'):
                    text += '\tif text := record["%s"]; text != "" {\n' % fname
                    text += GoCsvLoadGenerator.gen_field_array_assign_stmt(prefix, field['original_type_name'], fname,
                                                                           valuetext, 2)
                    text += '%s}\n' % '\t'
                elif origin_type_name.startswith('map'):
                    text += '\tif text := record["%s"]; text != "" {\n' % fname
                    text += GoCsvLoadGenerator.gen_field_map_assign_stmt(prefix, field['original_type_name'], fname,
                                                                         valuetext, 2)
                    text += '%s}\n' % '\t'
                else:
                    valuetext = 'record["%s"]' % fname
                    text += GoCsvLoadGenerator.gen_field_assign_stmt(prefix + field_name, typename, valuetext, 2, valuetext)
            idx += 1
            content += text

        content += '%sreturn nil\n' % '\t'
        content += '}\n\n'
        return content

    # 生成内部class的赋值方法
    @staticmethod
    def gen_inner_class_parse(struct, prefix, rec_name):
        inner_fields = struct['inner_fields']
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerFieldName]
        assert len(inner_class_type) > 0 and len(inner_var_name) > 0

        start = inner_fields['start']
        end = inner_fields['end']
        step = inner_fields['step']
        assert start > 0 and end > 0 and step > 1

        col = start
        content = '\tfor i := 1; i <= %d; i++ {\n' % ((end-start)/step)
        content += '\t\tvar off = strconv.Itoa(i)\n'
        content += '\t\tvar val %s\n' % inner_class_type
        for i in range(step):
            field = struct['fields'][col + i]
            origin_type = field['original_type_name']
            typename = lang.map_go_type(origin_type)
            field_name = strutil.remove_suffix_number(field['camel_case_name'])
            text = ''
            valuetext = '%s["%s" + off]' % (rec_name, field_name)
            if origin_type.startswith('array'):
                text += '\tif text := %s["%s"]; text != "" {\n' % (rec_name, field_name)
                text += GoCsvLoadGenerator.gen_field_array_assign_stmt('val.', origin_type, field_name, valuetext, 2)
                text += '%s}\n' % '\t'
            elif origin_type.startswith('map'):
                text += '\tif text := %s["%s"]; text != "" {\n' % (rec_name, field_name)
                text += GoCsvLoadGenerator.gen_field_map_assign_stmt('val.', origin_type, field_name, valuetext, 2)
                text += '\tif text := %s["%s"]; text != "" {\n' % (rec_name, field_name)
            else:
                text += GoCsvLoadGenerator.gen_field_assign_stmt('val.' + field_name, typename, valuetext, 2, valuetext)
            content += text
        content += '%s%s = append(%s%s, val)\n' % (prefix, inner_var_name, prefix, inner_var_name)
        content += '\t}\n'
        return content

    # 生成Load方法
    @staticmethod
    def gen_load_method(struct):
        return ''

    # 生成helper.go文件
    @staticmethod
    def gen_helper_file(main_filepath, ver, args):
        const_def = go_template.GO_CONST_TEMPLATE % (predef.PredefDelim1, predef.PredefDelim2)
        filepath = os.path.abspath(os.path.dirname(main_filepath))
        filename = filepath + os.path.sep + 'helper.go'
        content = go_template.GO_HELP_FILE_HEAD_TEMPLATE % (ver, args.package)
        content += go_template.GO_HELP_FILE_TEMPLATE + const_def
        strutil.save_content_if_not_same(filename, content, 'utf-8')
