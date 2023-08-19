# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import tabugen.typedef as types
import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.util.tableutil as tableutil


# 生成C#加载CSV文件数据代码
class CSharpCsvLoadGenerator:
    TAB_SPACE = '    '

    def __init__(self):
        pass

    def setup(self, name):
        pass

    # 生成array类型的赋值代码
    def gen_array_field_assign(self, prefix: str, typename: str, name: str, value_text: str, tabs: int) -> str:
        content = ''
        space = self.TAB_SPACE * tabs
        elem_type = types.array_element_type(typename)
        content += '%s{\n' % space
        content += '%s    var listVal = new List<%s>();\n' % (space, lang.map_cs_type(elem_type))
        content += '%s    var strArr = %s.Split("%s", StringSplitOptions.RemoveEmptyEntries);\n' % (
            space, value_text, predef.PredefDelim1)
        content += "%s    for(int i = 0; i < strArr.Length; i++) \n" % space
        content += '%s    {\n' % space
        expr = lang.map_cs_parse_expr(elem_type, 'strArr[i]')
        content += '%s        listVal.Add(%s);\n' % (space, expr)
        content += '%s    }\n' % space
        content += '%s    %s%s = listVal.ToArray();\n' % (space, prefix, name)
        content += '%s}\n' % space
        return content

    # 生成map类型的赋值代码
    def gen_map_field_assign(self, prefix: str, typename: str, name: str, row_name: str, tabs: int) -> str:
        space = self.TAB_SPACE * tabs
        key_type, val_type = types.map_key_value_types(typename)

        content = '%s{\n' % space
        content += '%s    var mapVal = new Dictionary<%s, %s>();\n' % (space, lang.map_cs_type(key_type), lang.map_cs_type(val_type))
        content += '%s    var kvList = %s.Split("%s", StringSplitOptions.RemoveEmptyEntries);\n' % (
            space, row_name, predef.PredefDelim1)
        content += "%s    for(int i = 0; i < kvList.Length; i++) \n" % space
        content += '%s    {\n' % space
        content += '%s        var pair = kvList[i].Split("%s", StringSplitOptions.RemoveEmptyEntries);\n' % (space, predef.PredefDelim2)
        content += '%s        if (pair.Length == 2) {\n' % space
        content += '%s            var key = %s;\n' % (space, lang.map_cs_parse_expr(key_type, 'pair[0]'))
        content += '%s            var val = %s;\n' % (space, lang.map_cs_parse_expr(val_type, 'pair[1]'))
        content += '%s            mapVal[key] = val;\n' % space
        content += '%s        }\n' % space
        content += '%s    }\n' % space
        content += '%s    %s%s = mapVal;\n' % (space, prefix, name)
        content += '%s}\n' % space
        return content

    # 生成字段加载代码
    def gen_field_assign(self, prefix: str, origin_typename: str, name: str, value_text: str, tabs: int) -> str:
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
        content = '%s{\n' % space
        content += '%s    var listVal = new List<%s>();\n' % (space, inner_class_type)
        content += '%s    for (int i = 1; i < %s.Count; i++)\n' % (space, rec_name)
        content += '%s    {\n' % space
        content += '%s        var val = new %s();\n' % (space, inner_class_type)
        content += '%s        string strVal = "";\n' % space
        for i in range(step):
            field = struct['fields'][col + i]
            origin_typename = field['original_type_name']
            field_name = tableutil.remove_field_suffix(field['camel_case_name'])
            text = '%s        if (%s.TryGetValue($"%s{i}", out strVal)) {\n' % (space, rec_name, field_name)
            text += self.gen_field_assign('val.', origin_typename, field_name, 'strVal', tabs+3)
            text += '%s        } else {\n' % space
            text += '%s            break; \n' % space
            text += '%s        }\n' % space
            content += text
        content += '%s        listVal.Add(val);\n' % space
        content += '%s    }\n' % space
        content += '%s    %s%s = listVal.ToArray();\n' % (space, prefix, inner_var_name)
        content += '%s}\n' % space
        return content

    # 生成`ParseFrom`方法
    def gen_parse_method(self, struct, tabs: int):
        inner_start_col = -1
        inner_end_col = -1
        inner_field_done = False
        if 'inner_fields' in struct:
            inner_start_col = struct['inner_fields']['start']
            inner_end_col = struct['inner_fields']['end']

        space = self.TAB_SPACE * tabs
        content = ''
        content += '%spublic void ParseFrom(Dictionary<string, string> record) \n' % space
        content += '%s{\n' % space
        for col, field in enumerate(struct['fields']):
            if inner_start_col <= col <= inner_end_col:
                if not inner_field_done:
                    content += self.gen_inner_fields_assign(struct, 'this.', 'record', tabs+1)
                    inner_field_done = True
            else:
                origin_typename = field['original_type_name']
                valuetext = 'record["%s"]' % field['name']
                content += self.gen_field_assign('this.', origin_typename, field['name'], valuetext, tabs+1)

        content += '%s}\n\n' % space
        return content

    # 生成KV模式的`ParseFrom`方法
    def gen_kv_parse_method(self, struct, tabs: int):
        keyidx = struct['options']['key_column']
        validx = struct['options']['value_column']
        typeidx = struct['options']['type_column']
        assert keyidx >= 0 and validx >= 0 and typeidx >= 0

        rows = struct['data_rows']
        space = self.TAB_SPACE * tabs

        content = ''
        content += '%s// parse %s from string fields\n' % (space, struct['name'])
        content += '%spublic void ParseFrom(Dictionary<string, string> fields)\n' % space
        content += '%s{\n' % space
        for row in rows:
            name = row[keyidx].strip()
            origin_typename = row[typeidx].strip()
            value_text = 'fields["%s"]' % name
            content += self.gen_field_assign('this.', origin_typename, name, value_text, tabs + 1)
        content += '%s}\n\n' % space
        return content

    def generate(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct, 1)
        else:
            return self.gen_parse_method(struct, 1)
