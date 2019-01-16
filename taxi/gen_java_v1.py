# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import codecs
import basegen
import predef
import descriptor
import lang
import util

# java生成器
class JavaV1Generator(basegen.CodeGeneratorBase):
    TAB_SPACE = '    '

    def __init__(self):
        pass

    @staticmethod
    def name():
        return "java-v1"

    def get_instance_data_name(self, name):
        return '_instance_%s' % name.lower()

    def gen_java_class(self, struct):
        content = ''

        fields = struct['fields']
        if struct['options'][predef.PredefParseKVMode]:
            fields = self.get_struct_kv_fields(struct)

        inner_class_done = False
        inner_typename = ''
        inner_var_name = ''
        inner_field_names, inner_fields = self.get_inner_class_fields(struct)
        if len(inner_fields) > 0:
            content += self.gen_cs_inner_class(struct, inner_fields)
            inner_type_class = struct["options"][predef.PredefInnerTypeClass]
            inner_var_name = struct["options"][predef.PredefInnerTypeName]
            inner_typename = 'ArrayList<%s>' % inner_type_class

        content += '// %s\n' % struct['comment']
        content += 'public class %s\n{\n' % struct['name']

        vec_done = False
        vec_names, vec_name = self.get_vec_field_range(struct)

        max_name_len = util.max_field_length(fields, 'name', None)
        max_type_len = util.max_field_length(fields, 'original_type_name', lang.map_java_type)
        if len(inner_typename) > max_type_len:
            max_type_len = len(inner_typename)

        for field in fields:
            field_name = field['name']
            if field_name in inner_field_names:
                if not inner_class_done:
                    typename = util.pad_spaces(inner_typename, max_type_len)
                    content += '    public %s %s = new %s(); \n' % (typename, inner_var_name, typename)
                    inner_class_done = True
            else:
                typename = lang.map_java_type(field['original_type_name'])
                assert typename != "", field['original_type_name']
                typename = util.pad_spaces(typename, max_type_len + 1)
                if field['name'] not in vec_names:
                    name = lang.name_with_default_java_value(field, typename)
                    name = util.pad_spaces(name, max_name_len + 8)
                    content += '    public %s %s // %s\n' % (typename, name, field['comment'])
                elif not vec_done:
                    name = '%s = new %s[%d];' % (vec_name, typename.strip(), len(vec_names))
                    name = util.pad_spaces(name, max_name_len + 8)
                    content += '    public %s[] %s // %s\n' % (typename.strip(), name, field['comment'])
                    vec_done = True

        return content

    # 静态变量
    def gen_static_data(self, struct):
        content = '\n'
        if struct['options'][predef.PredefParseKVMode]:
            content += '    private static %s instance_;\n' % struct['name']
            content += '    public static %s getInstance() { return instance_; }\n\n' % struct['name']
        else:
            content += '    private static ArrayList<%s> data_;\n' % struct['name']
            content += '    public static ArrayList<%s> getData() { return data_; } \n\n' % struct['name']
        return content

    # 生成赋值方法
    def gen_field_assgin_stmt(self, name, typename, valuetext, tabs):
        content = ''
        space = self.TAB_SPACE * tabs
        if typename.lower() == 'string':
            content += '%s%s = %s.trim();\n' % (space, name, valuetext)
        elif typename.lower().find('bool') >= 0:
            content += '%s%s = Boolean.parseBoolean(%s);\n' % (space, name, valuetext)
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
    def gen_field_array_assign_stmt(self, prefix, typename, name, row_name, array_delim, tabs):
        assert len(array_delim) == 1
        array_delim = array_delim.strip()
        if array_delim == '\\':
            array_delim = '\\\\'

        content = ''
        space = self.TAB_SPACE * tabs
        elem_type = descriptor.array_element_type(typename)
        elem_type = lang.map_java_type(elem_type)
        content += "%for(String item : %s.split('%s')) {\n" % (space, row_name, array_delim)
        content += self.gen_field_assgin_stmt('var value', elem_type, 'item', tabs + 1)
        content += '%s    %s%s.Add(value);\n' % (space, prefix, name)
        content += '%s}\n' % space
        return content

        # 生成map赋值
    def gen_field_map_assign_stmt(self, prefix, typename, name, row_name, map_delims, tabs):
        assert len(map_delims) == 2, map_delims
        delim1 = map_delims[0].strip()
        if delim1 == '\\':
            delim1 = '\\\\'
        delim2 = map_delims[1].strip()
        if delim2 == '\\':
            delim2 = '\\\\'

        space = self.TAB_SPACE * tabs
        k, v = descriptor.map_key_value_types(typename)
        key_type = lang.map_java_type(k)
        val_type = lang.map_java_type(v)

        content = ''
        content += "%for(String text : %s.split('%s')) {\n" % (space, row_name, delim1)
        content += '%s    if (text.isEmpty()) {\n' % space
        content += '%s        continue;\n' % space
        content += '%s    }\n' % space
        content += "%s    String[] item = text.split('%s');\n" % (space, delim2)
        prefix1 = '%s key' % key_type
        prefix2 = '%s value' % val_type
        content += self.gen_field_assgin_stmt(prefix1, key_type, 'item[0]', tabs + 1)
        content += self.gen_field_assgin_stmt(prefix2, val_type, 'item[1]', tabs + 1)
        content += '%s    %s%s[key] = value;\n' % (space, prefix, name)
        content += '%s}\n' % space
        return content

    # 生成KV模式的Parse方法
    def gen_kv_parse_method(self, struct):
        rows = struct['data-rows']
        keycol = struct['options'][predef.PredefKeyColumn]
        valcol = struct['options'][predef.PredefValueColumn]
        typcol = int(struct['options'][predef.PredefValueTypeColumn])
        assert keycol > 0 and valcol > 0 and typcol > 0

        keyidx, keyfield = self.get_field_by_column_index(struct, keycol)
        validx, valfield = self.get_field_by_column_index(struct, valcol)
        typeidx, typefield = self.get_field_by_column_index(struct, typcol)

        array_delim = struct['options'].get(predef.OptionArrayDelimeter, predef.DefaultArrayDelimiter)
        map_delims = struct['options'].get(predef.OptionMapDelimeters, predef.DefaultMapDelimiters)

        content = ''
        content += '%s// parse data object from csv rows\n' % self.TAB_SPACE
        content += '%spublic static %s ParseFromRows(String[][] rows)\n' % (
        self.TAB_SPACE, struct['camel_case_name'])
        content += '%s{\n' % self.TAB_SPACE
        content += '%sif (rows.length < %d) {\n' % (self.TAB_SPACE * 2, len(rows))
        content += '%sthrow new RuntimeException(String.format("%s: row length out of index, %%d < %d", rows.length));\n' % (
        self.TAB_SPACE * 3, struct['name'], len(rows))
        content += '%s}\n' % (self.TAB_SPACE * 2)
        content += '%s%s obj = new %s();\n' % (
        self.TAB_SPACE * 2, struct['camel_case_name'], struct['camel_case_name'])

        idx = 0
        for row in rows:
            content += '%sif (!rows[%d][%d].isEmpty()) {\n' % (self.TAB_SPACE * 2, idx, validx)
            name = rows[idx][keyidx].strip()
            name = util.camel_case(name)
            origin_typename = rows[idx][typeidx].strip()
            typename = lang.map_java_type(origin_typename)
            valuetext = 'rows[%d][%d]' % (idx, validx)
            # print('kv', name, origin_typename, valuetext)
            if origin_typename.startswith('array'):
                content += self.gen_field_array_assign_stmt('obj.', origin_typename, name, valuetext, array_delim,
                                                            3)
            elif origin_typename.startswith('map'):
                content += self.gen_field_map_assign_stmt('obj.', origin_typename, name, valuetext, map_delims, 3)
            else:
                content += self.gen_field_assgin_stmt('obj.' + name, typename, valuetext, 3)
            content += '%s}\n' % (self.TAB_SPACE * 2)
            idx += 1
        content += '%sreturn obj;\n' % (self.TAB_SPACE * 2)
        content += '%s}\n\n' % self.TAB_SPACE
        return content

    # 生成ParseFromRow方法
    def gen_parse_method(self, struct):
        content = ''
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct)

        array_delim = struct['options'].get(predef.OptionArrayDelimeter, predef.DefaultArrayDelimiter)
        map_delims = struct['options'].get(predef.OptionMapDelimeters, predef.DefaultMapDelimiters)

        vec_idx = 0
        vec_names, vec_name = self.get_vec_field_range(struct)

        inner_class_done = False
        inner_field_names, inner_fields = self.get_inner_class_fields(struct)

        content += '%s// parse data object from an csv row\n' % self.TAB_SPACE
        content += '%spublic static %s ParseFromRow(String[] row)\n' % (self.TAB_SPACE, struct['camel_case_name'])
        content += '%s{\n' % self.TAB_SPACE
        content += '%sif (row.length < %d) {\n' % (self.TAB_SPACE * 2, len(struct['fields']))
        content += '%sthrow new RuntimeException(String.format("%s: row length out of index %%d", row.length));\n' % (
        self.TAB_SPACE * 3, struct['name'])
        content += '%s}\n' % (self.TAB_SPACE * 2)
        content += '%s%s obj = new %s();\n' % (self.TAB_SPACE * 2, struct['camel_case_name'], struct['camel_case_name'])

        idx = 0
        prefix = 'obj.'
        for field in struct['fields']:
            field_name = field['name']
            if field_name in inner_field_names:
                if not inner_class_done:
                    inner_class_done = True
                    content += self.gen_cs_inner_class_assign(struct, prefix, inner_fields)
            else:
                content += '%sif (!row[%d].isEmpty()) {\n' % (self.TAB_SPACE*2, idx)
                origin_type_name = field['original_type_name']
                typename = lang.map_java_type(origin_type_name)
                valuetext = 'row[%d]' % idx
                if origin_type_name.startswith('array'):
                    content += self.gen_field_array_assign_stmt(prefix, origin_type_name, field_name, valuetext, array_delim, 3)
                elif origin_type_name.startswith('map'):
                    content += self.gen_field_map_assign_stmt(prefix, origin_type_name, field_name, valuetext, map_delims, 3)
                else:
                    if field_name in vec_names:
                        name = '%s[%d]' % (vec_name, vec_idx)
                        content += self.gen_field_assgin_stmt(prefix+name, typename, valuetext, 3)
                        vec_idx += 1
                    else:
                        content += self.gen_field_assgin_stmt(prefix+field_name, typename, valuetext, 3)
                content += '%s}\n' % (self.TAB_SPACE*2)
            idx += 1
        content += '%sreturn obj;\n' % (self.TAB_SPACE*2)
        content += '%s}\n\n' % self.TAB_SPACE
        return content

    # 生成内部类的parse
    def gen_inner_class_assign(self, struct, prefix, inner_fields):
        content = ''
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerTypeName]
        start, end, step = self.get_inner_class_range(struct)
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
            content += self.gen_field_assgin_stmt("item." + field['name'], typename, valuetext, 4)
            content += '            }\n'
        content += '            %s%s.add(item);\n' % (prefix, inner_var_name)
        content += '        }\n'
        return content

    # KV模式的load
    def gen_kv_struct_load_method(self, struct):
        rows = struct['data-rows']
        keycol = struct['options'][predef.PredefKeyColumn]
        valcol = struct['options'][predef.PredefValueColumn]
        typcol = int(struct['options'][predef.PredefValueTypeColumn])
        assert keycol > 0 and valcol > 0 and typcol > 0

        content = '%spublic static void LoadFromLines(String[] lines)\n' % self.TAB_SPACE
        content += '%s{\n' % self.TAB_SPACE
        content += '%sString[][] rows = new String[lines.length][];\n' % (self.TAB_SPACE * 2)
        content += '%sfor(int i = 0; i < lines.length; i++)\n' % (self.TAB_SPACE * 2)
        content += '%s{\n' % (self.TAB_SPACE * 2)
        content += '%sString line = lines[i];\n' % (self.TAB_SPACE * 3)
        content += '%srows[i] = line.split(",");\n' % (self.TAB_SPACE * 3)
        content += '%s}\n' % (self.TAB_SPACE * 2)
        content += '%sinstance_ = ParseFromRows(rows);\n' % (self.TAB_SPACE * 2)
        content += '%s}\n\n' % self.TAB_SPACE
        return content

    # 生成Load方法
    def gen_load_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_struct_load_method(struct)

        content = ''
        content = '%spublic static void LoadFromLines(String[] lines)\n' % self.TAB_SPACE
        content += '%s{\n' % self.TAB_SPACE
        content += '%data_ = new ArrayList<%s>();\n' % (self.TAB_SPACE * 2, struct['name'])
        content += '%for(String line : lines)\n' % (self.TAB_SPACE * 2)
        content += '%s{\n' % (self.TAB_SPACE * 2)
        content += "%svar row = line.Split(',');\n" % (self.TAB_SPACE * 3)
        content += "%svar obj = ParseFromRow(row);\n" % (self.TAB_SPACE * 3)
        content += "%sData.Add(obj);\n" % (self.TAB_SPACE * 3)
        content += '%s}\n' % (self.TAB_SPACE * 2)
        content += '%s}\n\n' % self.TAB_SPACE
        return content

    def generate_class(self, struct, params):
        content = '\n'
        content += self.gen_java_class(struct)
        content += self.gen_static_data(struct)
        content += self.gen_parse_method(struct)
        content += self.gen_load_method(struct)
        content += '}\n'
        return content

    def run(self, descriptors, args):
        params = util.parse_args(args)
        assert 'pkg' in params  # java must define package name

        class_dict = {}

        data_only = params.get(predef.OptionDataOnly, False)
        no_data = params.get(predef.OptionNoData, False)

        for struct in descriptors:
            print(util.current_time(), 'start generate', struct['source'])
            self.setup_comment(struct)
            self.setup_key_value_mode(struct)
            if not data_only:
                content = ''
                content += 'package %s;\n' % params['pkg']
                content += 'import java.util.*;\n'
                content += '\n'
                content += self.generate_class(struct, params)
                class_dict[struct['camel_case_name']] = content

        for name in class_dict:
            content = class_dict[name]
            filename = '%s.java' % name
            f = codecs.open(filename, 'w', 'utf-8')
            f.writelines(content)
            f.close()
