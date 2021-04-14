# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import tabugen.typedef as types
import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.util.strutil as strutil
import tabugen.util.structutil as structutil
import tabugen.generator.csharp.template as csharp_template


# 生成C#加载CSV文件数据代码
class CSharpCsvLoadGenerator:
    TAB_SPACE = '    '

    def __init__(self):
        self.array_delim = ','
        self.map_delims = [',', '=']
        self.config_manager_name = ''

    # 初始化array, map分隔符
    def setup(self, array_delim, map_delims, name):
        self.array_delim = array_delim
        self.map_delims = map_delims
        self.config_manager_name = name

    @staticmethod
    def get_data_member_name(self, name):
        return name + 'Data'

    # 字段比较
    @staticmethod
    def gen_equal_stmt(prefix, struct, key):
        keys = structutil.get_struct_keys(struct, key, lang.map_cs_type)
        args = []
        for tpl in keys:
            args.append('%s%s == %s' % (prefix, tpl[1], tpl[1]))
        return ' && '.join(args)

    # 生成赋值方法
    def gen_field_assign_stmt(self, name, typename, valuetext, tabs):
        content = ''
        space = self.TAB_SPACE * tabs
        if typename.lower() == 'string':
            content += '%s%s = %s.Trim();\n' % (space, name, valuetext)
        elif typename.lower().find('bool') >= 0:
            content += '%s%s = %s.ParseBool(%s);\n' % (space, name, self.config_manager_name, valuetext)
        else:
            content += '%s%s = %s.Parse(%s);\n' % (space, name, typename, valuetext)
        return content

    # 生成array赋值
    def gen_field_array_assign_stmt(self, prefix, typename, name, row_name, tabs):
        assert len(self.array_delim) == 1

        content = ''
        space = self.TAB_SPACE * tabs
        elem_type = types.array_element_type(typename)
        elem_type = lang.map_cs_type(elem_type)
        content += "%svar items = %s.Split(%s.TABUGEN_ARRAY_DELIM, StringSplitOptions.RemoveEmptyEntries);\n" % (
            space, row_name, self.config_manager_name)
        content += '%s%s%s = new %s[items.Length];\n' % (space, prefix, name, elem_type)
        content += "%sfor(int i = 0; i < items.Length; i++) \n" % space
        content += "%s{\n" % space
        content += self.gen_field_assign_stmt('var value', elem_type, 'items[i]', tabs + 1)
        content += '%s    %s%s[i] = value;\n' % (space, prefix, name)
        content += '%s}\n' % space
        return content

    # 生成map赋值
    def gen_field_map_assign_stmt(self, prefix, typename, name, row_name, tabs):
        assert len(self.map_delims) == 2

        space = self.TAB_SPACE * tabs
        k, v = types.map_key_value_types(typename)
        key_type = lang.map_cs_type(k)
        val_type = lang.map_cs_type(v)

        content = "%svar items = %s.Split(%s.TABUGEN_MAP_DELIM1, StringSplitOptions.RemoveEmptyEntries);\n" % (
            space, row_name, self.config_manager_name)
        content += '%s%s%s = new Dictionary<%s,%s>();\n' % (space, prefix, name, key_type, val_type)
        content += "%sfor(int i = 0; i < items.Length; i++) \n" % space
        content += '%s{\n' % space
        content += '%s    string text = items[i];\n' % space
        content += '%s    if (text.Length == 0) {\n' % space
        content += '%s        continue;\n' % space
        content += '%s    }\n' % space
        content += "%s    var item = text.Split(%s.TABUGEN_MAP_DELIM2, StringSplitOptions.RemoveEmptyEntries);\n" % (
            space, self.config_manager_name)
        content += '%s    if (items.Length == 2) {\n' % space
        content += self.gen_field_assign_stmt('var key', key_type, 'item[0]', tabs+1)
        content += self.gen_field_assign_stmt('var value', val_type, 'item[1]', tabs + 1)
        content += '%s    %s%s[key] = value;\n' % (self.TAB_SPACE * (tabs + 1), prefix, name)
        content += '%s    }\n' % space
        content += '%s}\n' % space
        return content

    # 生成KV模式的Parse方法
    def gen_kv_parse_method(self, struct):
        rows = struct['data_rows']
        keycol = struct['options'][predef.PredefKeyColumn]
        valcol = struct['options'][predef.PredefValueColumn]
        typcol = int(struct['options'][predef.PredefValueTypeColumn])
        assert keycol > 0 and valcol > 0 and typcol > 0

        keyidx = keycol - 1
        validx = valcol - 1
        typeidx = typcol - 1

        content = '\n'
        content += '%s// parse object fields from text rows\n' % self.TAB_SPACE
        content += '%spublic void ParseFromRows(List<List<string>> rows)\n' % self.TAB_SPACE
        content += '%s{\n' % self.TAB_SPACE
        content += '%sif (rows.Count < %d) {\n' % (self.TAB_SPACE*2, len(rows))
        content += '%sthrow new ArgumentException(string.Format("%s: row length out of index, {0} < %d", rows.Count));\n' % (
            self.TAB_SPACE*3, struct['name'], len(rows))
        content += '%s}\n' % (self.TAB_SPACE*2)

        idx = 0
        prefix = 'this.'
        for row in rows:
            name = rows[idx][keyidx].strip()
            name = strutil.camel_case(name)
            origin_typename = rows[idx][typeidx].strip()
            typename = lang.map_cs_type(origin_typename)
            valuetext = 'rows[%d][%d]' % (idx, validx)
            text = ''
            # print('kv', name, origin_typename, valuetext)
            if origin_typename.startswith('array'):
                text += '%s{\n' % (self.TAB_SPACE * 2)
                text += self.gen_field_array_assign_stmt(prefix, origin_typename, name, valuetext, 3)
                text += '%s}\n' % (self.TAB_SPACE * 2)
            elif origin_typename.startswith('map'):
                text += '%s{\n' % (self.TAB_SPACE * 2)
                text += self.gen_field_map_assign_stmt(prefix, origin_typename, name, valuetext, 3)
                text += '%s}\n' % (self.TAB_SPACE * 2)
            else:
                text += '%sif (rows[%d][%d].Length > 0) {\n' % (self.TAB_SPACE * 2, idx, validx)
                text += self.gen_field_assign_stmt(prefix + name, typename, valuetext, 3)
                text += '%s}\n' % (self.TAB_SPACE*2)
            content += text
            idx += 1
        content += '%s}\n' % self.TAB_SPACE
        return content

    # 生成ParseFromRow方法
    def gen_parse_method(self, struct):
        content = ''
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct)

        vec_idx = 0
        vec_names, vec_name = structutil.get_vec_field_range(struct)
        fields = structutil.enabled_fields(struct)

        inner_class_done = False
        inner_field_names, inner_fields = structutil.get_inner_class_mapped_fields(struct)

        content += '\n'
        content += '%s// parse object fields from a text row\n' % self.TAB_SPACE
        content += '%spublic void ParseFromRow(List<string> row)\n' % self.TAB_SPACE
        content += '%s{\n' % self.TAB_SPACE
        content += '%sif (row.Count < %d) {\n' % (self.TAB_SPACE*2, len(fields))
        content += '%sthrow new ArgumentException(string.Format("%s: row length too short {0}", row.Count));\n' % (
            self.TAB_SPACE * 3, struct['name'])
        content += '%s}\n' % (self.TAB_SPACE*2)

        idx = 0
        prefix = 'this.'
        for field in struct['fields']:
            if not field['enable']:
                continue
            text = ''
            field_name = field['name']
            if field_name in inner_field_names:
                if not inner_class_done:
                    inner_class_done = True
                    text += self.gen_cs_inner_class_assign(struct, prefix)
            else:
                origin_type_name = field['original_type_name']
                typename = lang.map_cs_type(origin_type_name)
                valuetext = 'row[%d]' % idx
                if origin_type_name.startswith('array'):
                    text += '%s{\n' % (self.TAB_SPACE * 2)
                    text += self.gen_field_array_assign_stmt(prefix, origin_type_name, field_name, valuetext, 3)
                    text += '%s}\n' % (self.TAB_SPACE * 2)
                elif origin_type_name.startswith('map'):
                    text += '%s{\n' % (self.TAB_SPACE * 2)
                    text += self.gen_field_map_assign_stmt(prefix, origin_type_name, field_name, valuetext, 3)
                    text += '%s}\n' % (self.TAB_SPACE * 2)
                else:
                    text += '%sif (row[%d].Length > 0) {\n' % (self.TAB_SPACE * 2, idx)
                    if field_name in vec_names:
                        name = '%s[%d]' % (vec_name, vec_idx)
                        text += self.gen_field_assign_stmt(prefix+name, typename, valuetext, 3)
                        vec_idx += 1
                    else:
                        text += self.gen_field_assign_stmt(prefix+field_name, typename, valuetext, 3)
                    text += '%s}\n' % (self.TAB_SPACE*2)
            idx += 1
            content += text
        content += '%s}\n' % self.TAB_SPACE
        return content

    # 生成内部类的parse
    def gen_cs_inner_class_assign(self, struct, prefix):
        content = ''
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerTypeName]
        inner_fields = structutil.get_inner_class_struct_fields(struct)
        start, end, step = structutil.get_inner_class_range(struct)
        assert start > 0 and end > 0 and step > 1
        content += '        %s%s = new %s[%d];\n' % (prefix, inner_var_name, inner_class_type, (end-start)/step)
        content += '        for (int i = %s, j = 0; i < %s; i += %s, j++) \n' % (start, end, step)
        content += '        {\n'
        content += '            %s item = new %s();\n' % (inner_class_type, inner_class_type)
        for n in range(step):
            field = inner_fields[n]
            origin_type = field['original_type_name']
            typename = lang.map_cs_type(origin_type)
            valuetext = 'row[i + %d]' % n
            content += '            if (row[i + %d].Length > 0) \n' % n
            content += '            {\n'
            content += self.gen_field_assign_stmt("item." + field['name'], typename, valuetext, 4)
            content += '            }\n'
        content += '            %s%s[j] = item;\n' % (prefix, inner_var_name)
        content += '        }\n'
        return content


    # 生成manager类型
    def gen_global_class(self, descriptors, args):
        content = ''
        content += csharp_template.CSHARP_MANAGER_TEMPLATE % (self.config_manager_name, args.out_csv_delim,
                                                              self.array_delim, self.map_delims[0], self.map_delims[1])
        content += '}\n\n'
        return content

    #
    def gen_source_method(self, struct):
        content = ''
        content += self.gen_parse_method(struct)
        return content
