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

        content += '%sfor _, item := range strings.Split(%s, TABUGEN_SEP_DELIM1) {\n' % (space, row_name)
        content += '%s    var value = %s(item)\n' % (space, lang.map_go_parse_fn(elem_type))
        content += '%s    %s%s = append(p.%s, value)\n' % (space, prefix, name, name)
        content += '%s}\n' % space
        return content

    # 生成map赋值
    @staticmethod
    def gen_field_map_assign_stmt(prefix, typename, name, row_name, tabs):
        space = '\t' * tabs
        k, v = types.map_key_value_types(typename)
        key_type = lang.map_go_type(k)
        val_type = lang.map_go_type(v)

        content = ''
        content += '%s%s%s = map[%s]%s{}\n' % (space, prefix, name, key_type, val_type)
        content += '%sfor _, text := range strings.Split(%s, TABUGEN_SEP_DELIM1) {\n' % (space, row_name)
        content += '%s    if text == "" {\n' % space
        content += '%s        continue\n' % space
        content += '%s    }\n' % space
        content += '%s    var pair = strings.Split(text, TABUGEN_SEP_DELIM2)\n' % space
        content += '%s    var key = %s(pair[0])\n' % (space, lang.map_go_parse_fn(key_type))
        content += '%s    var val = %s(pair[1])\n' % (space, lang.map_go_parse_fn(val_type))
        content += '%s    %s%s[key] = val\n' % (space, prefix, name)
        content += '%s}\n' % space
        return content

    # KV模式的ParseFromRow方法
    @staticmethod
    def gen_kv_parse_method(struct):
        content = ''
        rows = struct['data_rows']

        keyidx = predef.PredefKeyColumn
        validx = predef.PredefValueColumn
        typeidx = predef.PredefValueTypeColumn

        content += 'func (p *%s) ParseFromRows(rows [][]string) error {\n' % struct['camel_case_name']
        content += '\tif len(rows) < %d {\n' % len(rows)
        content += '\t\tlog.Panicf("%s:row length out of index, %%d < %d", len(rows))\n' % (struct['name'], len(rows))
        content += '\t}\n'

        idx = 0
        for row in rows:
            content += '\tif rows[%d][%d] != "" {\n' % (idx, validx)
            name = rows[idx][keyidx].strip()
            name = strutil.camel_case(name)
            origin_typename = rows[idx][typeidx].strip()
            typename = lang.map_go_type(origin_typename)
            valuetext = 'rows[%d][%d]' % (idx, validx)
            # print('kv', name, origin_typename, valuetext)
            if origin_typename.startswith('array'):
                content += GoCsvLoadGenerator.gen_field_array_assign_stmt('p.', origin_typename, name, valuetext, 2)
            elif origin_typename.startswith('map'):
                content += GoCsvLoadGenerator.gen_field_map_assign_stmt('p.', origin_typename, name, valuetext, 2)
            else:
                content += GoCsvLoadGenerator.gen_field_assign_stmt('p.' + name, typename, valuetext, 2, idx)
            content += '%s}\n' % '\t'
            idx += 1
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
        content += 'func (p *%s) ParseFromRow(row []string) error {\n' % struct['camel_case_name']
        content += '\tif len(row) < %d {\n' % len(struct['fields'])
        content += '\t\tlog.Panicf("%s: row length too short %%d", len(row))\n' % struct['name']
        content += '\t}\n'

        idx = 0
        prefix = 'p.'
        for field in struct['fields']:
            col = field['column_index']
            text = ''
            if inner_start_col <= col < inner_end_col:
                if not inner_field_done:
                    text = GoCsvLoadGenerator.gen_inner_class_parse(struct, prefix)
                    inner_field_done = True
            else:
                fname = field['name']
                text += '\tif row[%d] != "" {\n' % idx
                origin_type_name = field['original_type_name']
                typename = lang.map_go_type(origin_type_name)
                field_name = field['camel_case_name']
                valuetext = 'row[%d]' % idx
                if origin_type_name.startswith('array'):
                    text += GoCsvLoadGenerator.gen_field_array_assign_stmt(prefix, field['original_type_name'], fname,
                                                                           valuetext, 2)
                elif origin_type_name.startswith('map'):
                    text += GoCsvLoadGenerator.gen_field_map_assign_stmt(prefix, field['original_type_name'], fname,
                                                                         valuetext, 2)
                else:
                    text += GoCsvLoadGenerator.gen_field_assign_stmt(prefix + field_name, typename, valuetext, 2, 'row')
                text += '%s}\n' % '\t'

            idx += 1
            content += text

        content += '%sreturn nil\n' % '\t'
        content += '}\n\n'
        return content

    # 生成内部class的赋值方法
    @staticmethod
    def gen_inner_class_parse(struct, prefix):
        inner_fields = struct['inner_fields']
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerFieldName]
        assert len(inner_class_type) > 0 and len(inner_var_name) > 0
        start = inner_fields['start']
        end = inner_fields['end']
        step = inner_fields['step']
        assert start > 0 and end > 0 and step > 1

        content = ''
        content += '    for i := %s; i < %s; i += %s {\n' % (start, end, step)
        content += '        var val %s\n' % inner_class_type
        pos = 0
        for n in range(step):
            col = start + pos
            pos += 1
            field = struct['fields'][col]
            origin_type = field['original_type_name']
            typename = lang.map_go_type(origin_type)
            field_name = field['camel_case_name']
            text = 'row[i+%d]' % n
            content += '        if row[i+%d] != "" {\n' % n
            content += GoCsvLoadGenerator.gen_field_assign_stmt('val.' + field_name, typename, text, 3, 'row')
            content += '        }\n'
        content += '        %s%s = append(%s%s, val)\n' % (prefix, inner_var_name, prefix, inner_var_name)
        content += '    }\n'
        return content

    # KV模式下的Load方法
    @staticmethod
    def gen_load_method_kv(struct):
        content = ''
        content += go_template.GO_KV_LOAD_METHOD_TEMPLATE % (struct['name'], struct['name'],
                                                             struct['name'])
        return content

    # 生成Load方法
    @staticmethod
    def gen_load_method(struct):
        if struct['options'][predef.PredefParseKVMode]:
            return GoCsvLoadGenerator.gen_load_method_kv(struct)
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
