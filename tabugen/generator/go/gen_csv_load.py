"""
Copyright (C) 2018-present qi7chen@github. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

from argparse import Namespace
import tabugen.lang as lang
import tabugen.predef as predef
import tabugen.typedef as types
import tabugen.util.tableutil as tableutil
from tabugen.structs import Struct


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
            content += '%s%s%s = ParseSlice(%s, %s)\n' % (space, prefix, name, valuetext, pfname)
        elif types.is_map_type(origin_typename):
            key_type, val_type = types.map_key_value_types(origin_typename)
            pfname1 = lang.map_go_parse_func(key_type)
            pfname2 = lang.map_go_parse_func(val_type)
            content += '%s%s%s = ParseMap(%s, %s, %s)\n' % (space, prefix, name, valuetext, pfname1, pfname2)
        elif origin_typename == 'string':
            content += '%s%s%s = strings.TrimSpace(%s)\n' % (space, prefix, name, valuetext)
        else:
            typename = lang.map_go_type(origin_typename)
            pfname = lang.map_go_parse_func(typename)
            content += '%s%s%s = %s(%s)\n' % (space, prefix, name, pfname, valuetext)
        return content

    # KV模式生成`ParseFrom`方法
    def gen_kv_parse_method(self, struct: Struct, args: Namespace) -> str:
        keyidx = struct.get_column_index(predef.PredefKVKeyName)
        typeidx = struct.get_column_index(predef.PredefKVTypeName)

        content = ''
        content += 'func (p *%s) ParseFrom(table map[string]string) error {\n' % struct.camel_case_name
        rows = struct.data_rows
        for row in rows:
            name = row[keyidx].strip()
            origin_typename = row[typeidx].strip()
            if args.legacy:
                try:
                    legacy = int(origin_typename)
                    origin_typename = types.legacy_type_to_name(legacy)
                except ValueError:
                    pass
            valuetext = 'table["%s"]' % name
            content += self.gen_field_assign('p.', origin_typename, name, valuetext, 1)
        content += '%sreturn nil\n' % '\t'
        content += '}\n\n'
        return content

    # 生成`ParseFrom`方法
    def gen_parse_method(self, struct: Struct) -> str:
        content = ''
        content += 'func (p *%s) ParseRow(table *GDTable, row int) error {\n' % struct.camel_case_name
        for field in struct.fields:
            origin_typename = field.origin_type_name
            valuetext = 'table.GetCell("%s", row)' % field.name
            content += self.gen_field_assign('p.', origin_typename, field.name, valuetext, 1)

        for array in struct.array_fields:
            content += '\tfor col := 0; col < table.ColSize(); col++ {\n'
            content += '\t\tvar name = fmt.Sprintf("%s[%%d]", col)\n' % array.name
            content += '\t\tif !table.HasColumn(name) {\n'
            content += '\t\t\tbreak\n'
            content += '\t\t}\n'
            origin_typename = array.element_fields[0].origin_type_name
            content += self.gen_field_assign('', origin_typename, 'var elem', 'table.GetCell(name, row)', 2)
            content += '\t\tp.%s = append(p.%s, elem)\n' % (array.field_name, array.field_name)
            content += '\t}\n'

        content += '%sreturn nil\n' % '\t'
        content += '}\n\n'
        return content

    def generate(self, struct: Struct, args: Namespace) -> str:
        if struct.options[predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct, args)
        else:
            return self.gen_parse_method(struct)
