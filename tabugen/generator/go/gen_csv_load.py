# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import tabugen.typedef as types
import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.util.strutil as strutil
import tabugen.util.structutil as structutil
import tabugen.generator.go.template as go_template


# 生成Go加载CSV文件数据代码
class GoCsvLoadGenerator:
    TAB_SPACE = '\t'

    def __init__(self):
        self.array_delim = ','
        self.map_delims = [',', '=']

    # 初始化array, map分隔符
    def setup(self, array_delim, map_delims):
        self.array_delim = array_delim
        self.map_delims = map_delims

    # 生成赋值方法
    def gen_field_assign_stmt(self, name, typename, valuetext, tabs, tips):
        content = ''
        space = self.TAB_SPACE * tabs
        if typename == 'string':
            return '%s%s = %s\n' % (space, name, valuetext)
        else:
            content += '%svar value = parseStringAs(%s, %s)\n' % (space, lang.map_go_reflect_type(typename), valuetext)
            content += '%s%s = value.(%s)\n' % (space, name, typename)
        return content

    # 生成array赋值
    def gen_field_array_assign_stmt(self, prefix, typename, name, row_name, tabs):
        assert len(self.array_delim) == 1

        space = self.TAB_SPACE * tabs
        content = ''
        elem_type = types.array_element_type(typename)
        elem_type = lang.map_go_type(elem_type)

        content += '%sfor _, item := range strings.Split(%s, TABULAR_ARRAY_DELIM) {\n' % (space, row_name)
        content += '%s    var value = parseStringAs(%s, item)\n' % (space, lang.map_go_reflect_type(elem_type))
        content += '%s    %s%s = append(p.%s, value.(%s))\n' % (space, prefix, name, name, elem_type)
        content += '%s}\n' % space
        return content

    # 生成map赋值
    def gen_field_map_assign_stmt(self, prefix, typename, name, row_name, tabs):
        assert len(self.map_delims) == 2

        space = self.TAB_SPACE * tabs
        k, v = types.map_key_value_types(typename)
        key_type = lang.map_go_type(k)
        val_type = lang.map_go_type(v)

        content = ''
        content += '%s%s%s = map[%s]%s{}\n' % (space, prefix, name, key_type, val_type)
        content += '%sfor _, text := range strings.Split(%s, TABULAR_MAP_DELIM1) {\n' % (space, row_name)
        content += '%s    if text == "" {\n' % space
        content += '%s        continue\n' % space
        content += '%s    }\n' % space
        content += '%s    var items = strings.Split(text, TABULAR_MAP_DELIM2)\n' % space
        content += '%s    var value = parseStringAs(%s, items[0])\n' % (space, lang.map_go_reflect_type(key_type))
        content += '%s    var key = value.(%s)\n' % (space, key_type)
        content += '%s    value = parseStringAs(%s, items[1])\n' % (space, lang.map_go_reflect_type(val_type))
        content += '%s    var val = value.(%s)\n' % (space, val_type)
        content += '%s    %s%s[key] = val\n' % (space, prefix, name)
        content += '%s}\n' % space
        return content

    # KV模式的ParseFromRow方法
    def gen_kv_parse_method(self, struct):
        content = ''
        rows = struct['data_rows']
        keycol = struct['options'][predef.PredefKeyColumn]
        valcol = struct['options'][predef.PredefValueColumn]
        typcol = int(struct['options'][predef.PredefValueTypeColumn])
        assert keycol > 0 and valcol > 0 and typcol > 0

        keyidx = keycol - 1
        validx = valcol - 1
        typeidx = typcol - 1

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
                content += self.gen_field_array_assign_stmt('p.', origin_typename, name, valuetext, 2)
            elif origin_typename.startswith('map'):
                content += self.gen_field_map_assign_stmt('p.', origin_typename, name, valuetext, 2)
            else:
                content += self.gen_field_assign_stmt('p.' + name, typename, valuetext, 2, idx)
            content += '%s}\n' % self.TAB_SPACE
            idx += 1
        content += '%sreturn nil\n' % self.TAB_SPACE
        content += '}\n\n'
        return content

    # 生成ParseFromRow方法
    def gen_parse_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct)

        inner_class_done = False
        inner_field_names, inner_fields = structutil.get_inner_class_mapped_fields(struct)

        vec_idx = 0
        vec_names, vec_name = structutil.get_vec_field_range(struct)
        fields = structutil.enabled_fields(struct)

        content = ''
        content += 'func (p *%s) ParseFromRow(row []string) error {\n' % struct['camel_case_name']
        content += '\tif len(row) < %d {\n' % len(fields)
        content += '\t\tlog.Panicf("%s: row length too short %%d", len(row))\n' % struct['name']
        content += '\t}\n'

        idx = 0
        for field in struct['fields']:
            if not field['enable']:
                continue
            text = ''
            fname = field['name']
            prefix = 'p.'
            if fname in inner_field_names:
                if not inner_class_done:
                    inner_class_done = True
                    text += self.gen_inner_class_parse(struct, prefix)
            else:
                text += '\tif row[%d] != "" {\n' % idx
                origin_type_name = field['original_type_name']
                typename = lang.map_go_type(origin_type_name)
                field_name = field['camel_case_name']
                valuetext = 'row[%d]' % idx
                if origin_type_name.startswith('array'):
                    text += self.gen_field_array_assign_stmt(prefix, field['original_type_name'], fname, valuetext, 2)
                elif origin_type_name.startswith('map'):
                    text += self.gen_field_map_assign_stmt(prefix, field['original_type_name'], fname, valuetext, 2)
                else:
                    if field_name in vec_names:
                        name = '%s[%d]' % (vec_name, vec_idx)
                        text += self.gen_field_assign_stmt(prefix + name, typename, valuetext, 2, 'row')
                        vec_idx += 1
                    else:
                        text += self.gen_field_assign_stmt(prefix + field_name, typename, valuetext, 2, 'row')
                text += '%s}\n' % self.TAB_SPACE
            idx += 1
            content += text

        content += '%sreturn nil\n' % self.TAB_SPACE
        content += '}\n\n'
        return content

    # 生成内部class的赋值方法
    def gen_inner_class_parse(self, struct, prefix):
        content = ''
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerTypeName]
        inner_fields = structutil.get_inner_class_struct_fields(struct)
        start, end, step = structutil.get_inner_class_range(struct)
        assert start > 0 and end > 0 and step > 1
        content += '    for i := %s; i < %s; i += %s {\n' % (start, end, step)
        content += '        var item %s;\n' % inner_class_type
        for n in range(step):
            field = inner_fields[n]
            origin_type = field['original_type_name']
            typename = lang.map_go_type(origin_type)
            field_name = field['camel_case_name']
            valuetext = 'row[i + %d]' % n
            content += '        if row[i + %d] != "" {\n' % n
            content += self.gen_field_assign_stmt('item.' + field_name, typename, valuetext, 2, 'row')
            content += '        }\n'
        content += '        %s%s = append(%s%s, item);\n' % (prefix, inner_var_name, prefix, inner_var_name)
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
    def gen_load_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_load_method_kv(struct)
        return ''

    # 生成helper.go文件
    @staticmethod
    def gen_helper_file(main_filepath, ver, pkgname):
        filepath = os.path.abspath(os.path.dirname(main_filepath))
        filename = filepath + os.path.sep + 'helper.go'
        content = go_template.GO_HELP_FILE_HEAD_TEMPLATE % (ver, pkgname)
        content += go_template.GO_HELP_FILE_TEMPLATE
        strutil.save_content_if_not_same(filename, content, 'utf-8')
