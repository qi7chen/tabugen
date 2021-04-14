# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import tabugen.predef as predef
import tabugen.lang as lang
import tabugen.typedef as types
import tabugen.util.strutil as strutil
import tabugen.util.structutil as structutil
import tabugen.generator.java.template as java_template


# java加载CSV代码生成器
class JavaCsvLoadGenerator:
    TAB_SPACE = '    '

    def __init__(self):
        self.array_delim = ','
        self.map_delims = [',', '=']
        self.config_manager_name = ''

    # 初始化array, map分隔符
    def setup(self, array_delim, map_delims, class_name):
        map_delims[0] = strutil.escape_delimiter(map_delims[0])
        map_delims[1] = strutil.escape_delimiter(map_delims[1])
        self.array_delim = strutil.escape_delimiter(array_delim)
        self.map_delims = map_delims
        self.config_manager_name = class_name

    @staticmethod
    def get_instance_data_name(name):
        return '_instance_%s' % name.lower()



    # 生成赋值方法
    def gen_field_assign_stmt(self, name, typename, valuetext, tabs):
        content = ''
        space = self.TAB_SPACE * tabs
        if typename.lower() == 'string':
            content += '%s%s = %s.trim();\n' % (space, name, valuetext)
        elif typename.lower().find('bool') >= 0:
            content += '%s%s = %s.parseBool(%s);\n' % (space, name, self.config_manager_name, valuetext)
        else:
            table = {
                'byte': 'Byte.parseByte(%s)',
                'short': 'Short.parseShort(%s)',
                'int': 'Integer.parseInt(%s)',
                'long': 'Long.parseLong(%s)',
                'float': 'Float.parseFloat(%s)',
                'double': 'Double.parseDouble(%s)'
            }
            line = table[typename] % valuetext
            content += '%s%s = %s;\n' % (space, name, line)
        return content

    # 生成array赋值
    def gen_field_array_assign_stmt(self, prefix, typename, name, row_name, tabs):
        assert len(self.array_delim) == 1

        content = ''
        space = self.TAB_SPACE * tabs
        elem_type = types.array_element_type(typename)
        elem_type = lang.map_java_type(elem_type)
        content += '%sString[] kvList = %s.split(%s.TABULAR_ARRAY_DELIM);\n' % (space, row_name, self.config_manager_name)
        content += '%s%s[] list = new %s[kvList.length];\n' % (space, elem_type, elem_type)
        content += '%sfor (int i = 0; i < kvList.length; i++) {\n' % space
        content += '%s    if (!kvList[i].isEmpty()) {\n' % (self.TAB_SPACE * tabs)
        varname = '%s value' % elem_type
        content += self.gen_field_assign_stmt(varname, elem_type, 'kvList[i]', tabs + 2)
        content += '%s        list[i] = value;\n' % (self.TAB_SPACE * tabs)
        content += '%s    }\n' % (self.TAB_SPACE * tabs)
        content += '%s}\n' % space
        content += '%s%s%s = list;\n' % (space, prefix, name)
        return content

        # 生成map赋值
    def gen_field_map_assign_stmt(self, prefix, typename, name, row_name, tabs):
        assert len(self.map_delims) == 2

        space = self.TAB_SPACE * tabs
        k, v = types.map_key_value_types(typename)
        key_type = lang.map_java_type(k)
        val_type = lang.map_java_type(v)

        content = '%sString[] kvList = %s.split(%s.TABULAR_MAP_DELIM1);\n' % (space, row_name, self.config_manager_name)
        content += '%sfor(int i = 0; i < kvList.length; i++) {\n' % space
        content += '%s    String text = kvList[i];\n' % space
        content += '%s    if (text.isEmpty()) {\n' % space
        content += '%s        continue;\n' % space
        content += '%s    }\n' % space
        content += '%s    String[] item = text.split(%s.TABULAR_MAP_DELIM2);\n' % (space, self.config_manager_name)
        prefix1 = '%s key' % key_type
        prefix2 = '%s value' % val_type
        content += self.gen_field_assign_stmt(prefix1, key_type, 'item[0]', tabs + 1)
        content += self.gen_field_assign_stmt(prefix2, val_type, 'item[1]', tabs + 1)
        content += '%s    %s%s.put(key, value);\n' % (space, prefix, name)
        content += '%s}\n' % space
        return content

    # 生成内部类的parse
    def gen_java_inner_class_assign(self, struct, prefix):
        content = ''
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerTypeName]
        inner_fields = structutil.get_inner_class_struct_fields(struct)
        start, end, step = structutil.get_inner_class_range(struct)
        assert start > 0 and end > 0 and step > 1
        content += '        for (int i = %s; i < %s; i += %s) \n' % (start, end, step)
        content += '        {\n'
        content += '            %s item = new %s();\n' % (inner_class_type, inner_class_type)
        for n in range(step):
            field = inner_fields[n]
            origin_type = field['original_type_name']
            typename = lang.map_java_type(origin_type)
            valuetext = 'record.get(i + %d)' % n
            content += '            if (!record.get(i + %d).isEmpty()) \n' % n
            content += '            {\n'
            content += self.gen_field_assign_stmt("item." + field['name'], typename, valuetext, 4)
            content += '            }\n'
        content += '            %s%s.add(item);\n' % (prefix, inner_var_name)
        content += '        }\n'
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

        content = ''
        content += '%s// parse fields data from text records\n' % self.TAB_SPACE
        content += '%spublic void parseFrom(List<CSVRecord> records)\n' % self.TAB_SPACE
        content += '%s{\n' % self.TAB_SPACE
        content += '%s    if (records.size() < %d) {\n' % (self.TAB_SPACE, len(rows))
        content += '%s        throw new RuntimeException(String.format("%s: records length too short, %%d < %d", records.size()));\n' % (
            self.TAB_SPACE, struct['name'], len(rows))
        content += '%s}\n' % (self.TAB_SPACE * 2)

        idx = 0
        for row in rows:
            name = rows[idx][keyidx].strip()
            name = strutil.camel_case(name)
            origin_typename = rows[idx][typeidx].strip()
            typename = lang.map_java_type(origin_typename)
            valuetext = 'records.get(%d).get(%d)' % (idx, validx)
            # print('kv', name, origin_typename, valuetext)
            if origin_typename.startswith('array'):
                content += '%s{\n' % (self.TAB_SPACE * 2)
                content += self.gen_field_array_assign_stmt('this.', origin_typename, name, valuetext, 3)
                content += '%s}\n' % (self.TAB_SPACE * 2)
            elif origin_typename.startswith('map'):
                content += '%s{\n' % (self.TAB_SPACE * 2)
                content += self.gen_field_map_assign_stmt('this.', origin_typename, name, valuetext, 3)
                content += '%s}\n' % (self.TAB_SPACE * 2)
            else:
                content += '%sif (!records.get(%d).get(%d).isEmpty()) {\n' % (self.TAB_SPACE * 2, idx, validx)
                content += self.gen_field_assign_stmt('this.' + name, typename, valuetext, 3)
                content += '%s}\n' % (self.TAB_SPACE * 2)
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

        inner_class_done = False
        inner_field_names, inner_fields = structutil.get_inner_class_mapped_fields(struct)
        fields = structutil.enabled_fields(struct)

        content += '%s// parse fields data from record\n' % self.TAB_SPACE
        content += '%spublic void parseFrom(CSVRecord record)\n' % self.TAB_SPACE
        content += '%s{\n' % self.TAB_SPACE
        content += '%sif (record.size() < %d) {\n' % (self.TAB_SPACE * 2, len(fields))
        content += '%sthrow new RuntimeException(String.format("%s: record length too short %%d", record.size()));\n' % (
        self.TAB_SPACE * 3, struct['name'])
        content += '%s}\n' % (self.TAB_SPACE * 2)

        idx = 0
        prefix = 'this.'
        for field in struct['fields']:
            if not field['enable']:
                continue
            field_name = field['name']
            text = ''
            if field_name in inner_field_names:
                if not inner_class_done:
                    inner_class_done = True
                    content += self.gen_java_inner_class_assign(struct, prefix)
            else:
                origin_type_name = field['original_type_name']
                typename = lang.map_java_type(origin_type_name)
                valuetext = 'record.get(%d)' % idx
                if origin_type_name.startswith('array'):
                    text += '%s{\n' % (self.TAB_SPACE * 2)
                    text += self.gen_field_array_assign_stmt(prefix, origin_type_name, field_name, valuetext, 3)
                    text += '%s}\n' % (self.TAB_SPACE * 2)
                elif origin_type_name.startswith('map'):
                    text += '%s{\n' % (self.TAB_SPACE * 2)
                    text += self.gen_field_map_assign_stmt(prefix, origin_type_name, field_name, valuetext, 3)
                    text += '%s}\n' % (self.TAB_SPACE * 2)
                else:
                    text += '%sif (!record.get(%d).isEmpty()) {\n' % (self.TAB_SPACE * 2, idx)
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
    def gen_inner_class_assign(self, struct, prefix, inner_fields):
        content = ''
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerTypeName]
        start, end, step = structutil.get_inner_class_range(struct)
        assert start > 0 and end > 0 and step > 1
        content += '        for (int i = %s; i < %s; i += %s) \n' % (start, end, step)
        content += '        {\n'
        content += '            %s item = new %s();\n' % (inner_class_type, inner_class_type)
        for n in range(step):
            field = inner_fields[n]
            origin_type = field['original_type_name']
            typename = lang.map_java_type(origin_type)
            valuetext = 'row[i + %d]' % n
            content += '            if (!row[i + %d].isEmpty()) \n' % n
            content += '            {\n'
            content += self.gen_field_assign_stmt("item." + field['name'], typename, valuetext, 4)
            content += '            }\n'
        content += '            %s%s.add(item);\n' % (prefix, inner_var_name)
        content += '        }\n'
        return content


    # 字段比较
    def gen_equal_stmt(self, prefix, struct, key):
        keys = structutil.get_struct_keys(struct, key, lang.map_java_type)
        args = []
        for tpl in keys:
            if lang.is_java_primitive_type(tpl[0]):
                args.append('%s%s == %s' % (prefix, tpl[1], tpl[1]))
            else:
                args.append('%s%s.equals(%s)' % (prefix, tpl[1], tpl[1]))
        return ' && '.join(args)

