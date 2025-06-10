# Copyright (C) 2018-present qi7chen@github. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

from argparse import Namespace
import tabugen.typedef as types
import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.util.tableutil as tableutil
from tabugen.structs import Struct


# 生成C#加载CSV文件数据代码
class CSharpCsvLoadGenerator:
    TAB_SPACE = '    '

    def __init__(self):
        pass

    def setup(self, name):
        pass


    # 生成字段加载代码
    def gen_field_assign1(self, prefix: str, origin_typename: str, name: str, value_text: str, tabs: int) -> str:
        content = ''
        space = self.TAB_SPACE * tabs
        if types.is_array_type(origin_typename):
            elem_type = lang.map_cs_type(types.array_element_type(origin_typename))
            content += '%s%s%s = Conv.ParseArray<%s>(%s);\n' % (space, prefix, name, elem_type, value_text)
        elif types.is_map_type(origin_typename):
            key_type, val_type = types.map_key_value_types(origin_typename)
            key_type = lang.map_cs_type(key_type)
            val_type = lang.map_cs_type(val_type)
            content += '%s%s%s = Conv.ParseMap<%s, %s>(%s);\n' % (space, prefix, name, key_type, val_type, value_text)
        elif origin_typename == 'string':
            content += '%s%s%s = %s.Trim();\n' % (space, prefix, name, value_text)
        else:
            func_name = lang.map_cs_parse_func(origin_typename)
            content += '%s%s%s = %s(%s);\n' % (space, prefix, name, func_name, value_text)
        return content

    def gen_field_assign2(self, prefix: str, origin_typename: str, field_name: str,  tabs: int) -> str:
        content = ''
        space = self.TAB_SPACE * tabs
        if types.is_array_type(origin_typename):
            elem_type = lang.map_cs_type(types.array_element_type(origin_typename))
            value_text = 'table.GetRowCell("%s", rowIndex)' % field_name
            content += '%s%s%s = Conv.ParseArray<%s>(%s);\n' % (space, prefix, field_name, elem_type, value_text)
        elif types.is_map_type(origin_typename):
            key_type, val_type = types.map_key_value_types(origin_typename)
            key_type = lang.map_cs_type(key_type)
            val_type = lang.map_cs_type(val_type)
            value_text = 'table.GetRowCell("%s", rowIndex)' % field_name
            content += '%s%s%s = Conv.ParseMap<%s, %s>(%s);\n' % (space, prefix, field_name, key_type, val_type, value_text)
        elif origin_typename == 'string':
            content += '%s%s%s = table.GetRowCell("%s", rowIndex);\n' % (space, prefix, field_name, field_name)
        else:
            func_name = lang.map_cs_parse_func(origin_typename)
            value_text = 'table.GetRowCell("%s", rowIndex)' % field_name
            content += '%s%s%s = %s(%s);\n' % (space, prefix, field_name, func_name, value_text)
        return content

    # 生成`ParseFrom`方法
    def gen_parse_method(self, struct: Struct, args: Namespace) -> str:
        space = self.TAB_SPACE
        content = ''
        content += '%spublic void ParseRow(IDataFrame table, int rowIndex) \n' % space
        content += '%s{\n' % space
        for field in struct.fields:
            origin_typename = field.origin_type_name
            valuetext = 'table.GetCell("%s", row)' % field.name
            content += self.gen_field_assign2('this.', origin_typename, field.name, 2)

        space = self.TAB_SPACE * 2
        for array in struct.array_fields:
            content += '%sfor (int col = 0; col < table.ColumnCount; col++) {\n' % space
            content += '%s    var name = string.Format("%s[{}]", col);\n' % (space, array.name)
            content += '%s    if (!table.HasColumn(name)) {\n' % space
            content += '%s        break;\n' % space
            content += '%s    }\n' % space
            origin_typename = array.element_fields[0].origin_type_name
            cs_type = lang.map_cs_type(origin_typename)
            if origin_typename == 'string':
                content += '%s    var elem = table.GetRowCell(name, rowIndex);\n' % space
            else:
                func_name = lang.map_cs_parse_func(origin_typename)
                value_text = 'table.GetRowCell("%s", rowIndex)' % array.field_name
                content += '%s    var elem = %s(%s);\n' % (space, func_name, value_text)
            content += '%s    this.%s.Add(elem);\n' % (space, array.field_name)
            content += '%s}\n' % space

        content += '%s}\n\n' % self.TAB_SPACE
        return content

    # 生成KV模式的`ParseFrom`方法
    def gen_kv_parse_method(self, struct: Struct, args: Namespace):
        tabs = 1
        space = self.TAB_SPACE * tabs

        content = ''
        content += '%spublic void ParseFrom(IDataFrame table)\n' % space
        content += '%s{\n' % space
        for field in struct.kv_fields:
            origin_typename = field.origin_type_name
            if args.legacy:
                try:
                    legacy = int(origin_typename)
                    origin_typename = types.legacy_type_to_name(legacy)
                except ValueError:
                    pass
            valuetext = 'table.GetKeyField("%s")' % field.name
            content += self.gen_field_assign1('this.', origin_typename, field.name, valuetext, 2)
        content += '%s}\n\n' % space
        return content

    def generate(self, struct: Struct, args: Namespace):
        if struct.options[predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct, args)
        else:
            return self.gen_parse_method(struct, args)
