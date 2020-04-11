# Copyright (C) 2018-present prototyped.cn. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import taksi.descriptor.predef as predef
import taksi.descriptor.lang as lang
import taksi.descriptor.types as types
import taksi.descriptor.strutil as strutil
import taksi.generator.genutil as genutil
import taksi.version as version
from taksi.generator.java.gen_struct import JavaStructGenerator

JAVA_CLASS_TEMPLATE = """

import java.io.*;
import java.util.*;
import java.util.function.Function;

public class %s {

    final public static String LF = "\\n"; // line feed
    
    // parse text to boolean value
    public static boolean parseBool(String text) {
        if (!text.isEmpty()) {
            return text.equals("1") ||
                    text.equalsIgnoreCase("on") ||
                    text.equalsIgnoreCase("yes")  ||
                    text.equalsIgnoreCase("true");
        }
        return false;
    }

    public static String readFileContent(String filepath) {
        StringBuilder sb = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new FileReader(filepath))) {
            String line = null;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
                sb.append(LF); // line break
            }
        } catch(IOException ex) {
            System.err.println(ex.getMessage());
            ex.printStackTrace();
        }
        return sb.toString();
    }
    
    // you can set your own file content reader
    public static Function<String, String> reader;
    
    public static String[] readFileToTextLines(String filename) {
        if (reader == null) {
            reader = (filepath)-> readFileContent(filepath);
        }
        String content = reader.apply(filename);
        return content.split(LF, -1);
    }    

"""


# java生成器
class JavaCsvLoadGenerator(JavaStructGenerator):
    TAB_SPACE = '    '

    def __init__(self):
        pass

    @staticmethod
    def name():
        return "java-csv"

    def get_instance_data_name(self, name):
        return '_instance_%s' % name.lower()

    # 静态变量
    def gen_static_data(self, struct):
        content = '\n'
        if struct['options'][predef.PredefParseKVMode]:
            content += '    private static %s instance_;\n' % struct['name']
            content += '    public static %s getInstance() { return instance_; }\n\n' % struct['name']
        else:
            content += '    private static List<%s> data_ = new ArrayList<>();\n' % struct['name']
            content += '    public static List<%s> getData() { return data_; } \n\n' % struct['name']
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
        elem_type = types.array_element_type(typename)
        elem_type = lang.map_java_type(elem_type)
        content += '%sString[] tokens = %s.split("\\\\%s");\n' % (space, row_name, array_delim)
        content += '%s%s[] list = new %s[tokens.length];\n' % (space, elem_type, elem_type)
        content += '%sfor (int i = 0; i < tokens.length; i++) {\n' % space
        content += '%s    if (!tokens[i].isEmpty()) {\n' % (self.TAB_SPACE * tabs)
        varname = '%s value' % elem_type
        content += self.gen_field_assgin_stmt(varname, elem_type, 'tokens[i]', tabs + 2)
        content += '%s        list[i] = value;\n' % (self.TAB_SPACE * tabs)
        content += '%s    }\n' % (self.TAB_SPACE * tabs)
        content += '%s}\n' % space
        content += '%s%s%s = list;\n' % (space, prefix, name)
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
        k, v = types.map_key_value_types(typename)
        key_type = lang.map_java_type(k)
        val_type = lang.map_java_type(v)

        content = '%sString[] tokens = %s.split("\\\\%s");\n' % (space, row_name, delim1)
        content += '%sfor(int i = 0; i < tokens.length; i++) {\n' % space
        content += '%s    String text = tokens[i];\n' % space
        content += '%s    if (text.isEmpty()) {\n' % space
        content += '%s        continue;\n' % space
        content += '%s    }\n' % space
        content += '%s    String[] item = text.split("\\\\%s");\n' % (space, delim2)
        prefix1 = '%s key' % key_type
        prefix2 = '%s value' % val_type
        content += self.gen_field_assgin_stmt(prefix1, key_type, 'item[0]', tabs + 1)
        content += self.gen_field_assgin_stmt(prefix2, val_type, 'item[1]', tabs + 1)
        content += '%s    %s%s.put(key, value);\n' % (space, prefix, name)
        content += '%s}\n' % space
        return content

    # 生成内部类的parse
    def gen_java_inner_class_assign(self, struct, prefix):
        content = ''
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerTypeName]
        inner_fields = genutil.get_inner_class_struct_fields(struct)
        start, end, step = genutil.get_inner_class_range(struct)
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

    # 生成KV模式的Parse方法
    def gen_kv_parse_method(self, struct):
        rows = struct['data_rows']
        keycol = struct['options'][predef.PredefKeyColumn]
        valcol = struct['options'][predef.PredefValueColumn]
        typcol = int(struct['options'][predef.PredefValueTypeColumn])
        assert keycol > 0 and valcol > 0 and typcol > 0

        keyidx, keyfield = genutil.get_field_by_column_index(struct, keycol)
        validx, valfield = genutil.get_field_by_column_index(struct, valcol)
        typeidx, typefield = genutil.get_field_by_column_index(struct, typcol)

        array_delim = struct['options'].get(predef.OptionArrayDelimeter, predef.DefaultArrayDelimiter)
        map_delims = struct['options'].get(predef.OptionMapDelimeters, predef.DefaultMapDelimiters)

        content = ''
        content += '%s// parse fields data from text rows\n' % self.TAB_SPACE
        content += '%spublic void parseFromRows(String[][] rows)\n' % self.TAB_SPACE
        content += '%s{\n' % self.TAB_SPACE
        content += '%s    if (rows.length < %d) {\n' % (self.TAB_SPACE, len(rows))
        content += '%s        throw new RuntimeException(String.format("%s: row length out of index, %%d < %d", rows.length));\n' % (
            self.TAB_SPACE, struct['name'], len(rows))
        content += '%s}\n' % (self.TAB_SPACE * 2)

        idx = 0
        for row in rows:
            name = rows[idx][keyidx].strip()
            name = strutil.camel_case(name)
            origin_typename = rows[idx][typeidx].strip()
            typename = lang.map_java_type(origin_typename)
            valuetext = 'rows[%d][%d]' % (idx, validx)
            # print('kv', name, origin_typename, valuetext)
            if origin_typename.startswith('array'):
                content += '%s{\n' % (self.TAB_SPACE * 2)
                content += self.gen_field_array_assign_stmt('this.', origin_typename, name, valuetext, array_delim, 3)
                content += '%s}\n' % (self.TAB_SPACE * 2)
            elif origin_typename.startswith('map'):
                content += '%s{\n' % (self.TAB_SPACE * 2)
                content += self.gen_field_map_assign_stmt('this.', origin_typename, name, valuetext, map_delims, 3)
                content += '%s}\n' % (self.TAB_SPACE * 2)
            else:
                content += '%sif (!rows[%d][%d].isEmpty()) {\n' % (self.TAB_SPACE * 2, idx, validx)
                content += self.gen_field_assgin_stmt('this.' + name, typename, valuetext, 3)
                content += '%s}\n' % (self.TAB_SPACE * 2)
            idx += 1
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
        vec_names, vec_name = genutil.get_vec_field_range(struct)

        inner_class_done = False
        inner_field_names, inner_fields = genutil.get_inner_class_mapped_fields(struct)

        content += '%s// parse fields data from text row\n' % self.TAB_SPACE
        content += '%spublic void parseFromRow(String[] row)\n' % self.TAB_SPACE
        content += '%s{\n' % self.TAB_SPACE
        content += '%sif (row.length < %d) {\n' % (self.TAB_SPACE * 2, len(struct['fields']))
        content += '%sthrow new RuntimeException(String.format("%s: row length out of index %%d", row.length));\n' % (
        self.TAB_SPACE * 3, struct['name'])
        content += '%s}\n' % (self.TAB_SPACE * 2)

        idx = 0
        prefix = 'this.'
        for field in struct['fields']:
            field_name = field['name']
            if field_name in inner_field_names:
                if not inner_class_done:
                    inner_class_done = True
                    content += self.gen_java_inner_class_assign(struct, prefix)
            else:
                origin_type_name = field['original_type_name']
                typename = lang.map_java_type(origin_type_name)
                valuetext = 'row[%d]' % idx
                if origin_type_name.startswith('array'):
                    content += '%s{\n' % (self.TAB_SPACE * 2)
                    content += self.gen_field_array_assign_stmt(prefix, origin_type_name, field_name, valuetext, array_delim, 3)
                    content += '%s}\n' % (self.TAB_SPACE * 2)
                elif origin_type_name.startswith('map'):
                    content += '%s{\n' % (self.TAB_SPACE * 2)
                    content += self.gen_field_map_assign_stmt(prefix, origin_type_name, field_name, valuetext, map_delims, 3)
                    content += '%s}\n' % (self.TAB_SPACE * 2)
                else:
                    content += '%sif (!row[%d].isEmpty()) {\n' % (self.TAB_SPACE * 2, idx)
                    if field_name in vec_names:
                        name = '%s[%d]' % (vec_name, vec_idx)
                        content += self.gen_field_assgin_stmt(prefix+name, typename, valuetext, 3)
                        vec_idx += 1
                    else:
                        content += self.gen_field_assgin_stmt(prefix+field_name, typename, valuetext, 3)
                    content += '%s}\n' % (self.TAB_SPACE*2)
            idx += 1
        content += '%s}\n\n' % self.TAB_SPACE
        return content

    # 生成内部类的parse
    def gen_inner_class_assign(self, struct, prefix, inner_fields):
        content = ''
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerTypeName]
        start, end, step = genutil.get_inner_class_range(struct)
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
        rows = struct['data_rows']
        keycol = struct['options'][predef.PredefKeyColumn]
        valcol = struct['options'][predef.PredefValueColumn]
        typcol = int(struct['options'][predef.PredefValueTypeColumn])
        assert keycol > 0 and valcol > 0 and typcol > 0

        content = '%spublic static void loadFromFile(String filepath)\n' % self.TAB_SPACE
        content += '%s{\n' % self.TAB_SPACE
        content += '%s    String[] lines = %s.readFileToTextLines(filepath);\n' % (self.TAB_SPACE, strutil.config_manager_name)
        content += '%s    String[][] rows = new String[lines.length][];\n' % self.TAB_SPACE
        content += '%s    for(int i = 0; i < lines.length; i++)\n' % self.TAB_SPACE
        content += '%s    {\n' % self.TAB_SPACE
        content += '%s        String line = lines[i];\n' % self.TAB_SPACE
        content += '%s        rows[i] = line.split("\\\\,", -1);\n' % self.TAB_SPACE
        content += '%s    }\n' % self.TAB_SPACE
        content += '%s    instance_ = new %s();\n' % (self.TAB_SPACE, struct['name'])
        content += '%s    instance_.parseFromRows(rows);\n' % self.TAB_SPACE
        content += '%s}\n\n' % self.TAB_SPACE
        return content

    # 生成Load方法
    def gen_load_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_struct_load_method(struct)

        content = ''
        content = '%spublic static void loadFromFile(String filepath)\n' % self.TAB_SPACE
        content += '%s{\n' % self.TAB_SPACE
        content += '%s    data_.clear();\n' % self.TAB_SPACE
        content += '%s    String[] lines = %s.readFileToTextLines(filepath);\n' % (self.TAB_SPACE, strutil.config_manager_name)
        content += '%s    for(String line : lines)\n' % self.TAB_SPACE
        content += '%s    {\n' % self.TAB_SPACE
        content += '%s        if (line.isEmpty())\n' % self.TAB_SPACE
        content += '%s            continue;\n' % self.TAB_SPACE
        content += '%s        String[] row = line.split("\\\\,", -1);\n' % self.TAB_SPACE  #
        content += '%s        %s obj = new %s();\n' % (self.TAB_SPACE, struct['name'], struct['name'])
        content += "%s        obj.parseFromRow(row);\n" % self.TAB_SPACE
        content += "%s        data_.add(obj);\n" % self.TAB_SPACE
        content += '%s     }\n' % self.TAB_SPACE
        content += '%s}\n\n' % self.TAB_SPACE
        return content

    # 字段比较
    def gen_equal_stmt(self, prefix, struct, key):
        keys = genutil.get_struct_keys(struct, key, lang.map_java_type)
        args = []
        for tpl in keys:
            if lang.is_java_primitive_type(tpl[0]):
                args.append('%s%s == %s' % (prefix, tpl[1], tpl[1]))
            else:
                args.append('%s%s.equals(%s)' % (prefix, tpl[1], tpl[1]))
        return ' && '.join(args)

    # 生成getItemBy()方法
    def gen_get_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return ''

        keys = genutil.get_struct_keys(struct, predef.PredefGetMethodKeys, lang.map_java_type)
        if len(keys) == 0:
            return ''

        formal_param = []
        arg_names = []
        for tpl in keys:
            typename = tpl[0]
            formal_param.append('%s %s' % (typename, tpl[1]))
            arg_names.append(tpl[1])

        content = ''
        content += '    // get an item by key\n'
        content += '    public static %s getItemBy(%s)\n' % (struct['name'], ', '.join(formal_param))
        content += '    {\n'
        content += '        for (%s item : data_)\n' % struct['name']
        content += '        {\n'
        content += '            if (%s)\n' % self.gen_equal_stmt('item.', struct, 'get-keys')
        content += '            {\n'
        content += '                return item;\n'
        content += '            }\n'
        content += '        }\n'
        content += '        return null;\n'
        content += '    }\n\n'
        return content

        # 生成getRange()方法
    def gen_range_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return ''

        if predef.PredefRangeMethodKeys not in struct['options']:
            return ''

        keys = genutil.get_struct_keys(struct, predef.PredefRangeMethodKeys, lang.map_java_type)
        assert len(keys) > 0

        formal_param = []
        arg_names = []
        for tpl in keys:
            typename = tpl[0]
            formal_param.append('%s %s' % (typename, tpl[1]))
            arg_names.append(tpl[1])

        content = ''
        content += '    // get a range of items by key\n'
        content += '    public static ArrayList<%s> getRange(%s)\n' % (struct['name'], ', '.join(formal_param))
        content += '    {\n'
        content += '        ArrayList<%s> range = new ArrayList<%s>();\n' % (struct['name'], struct['name'])
        content += '        for (%s item : data_)\n' % struct['name']
        content += '        {\n'
        content += '            if (%s)\n' % self.gen_equal_stmt('item.', struct, 'range-keys')
        content += '            {\n'
        content += '                range.add(item);\n'
        content += '            }\n'
        content += '        }\n'
        content += '        return range;\n'
        content += '    }\n\n'
        return content

    # 生成对象及方法
    def generate_class(self, struct, params):
        content = '\n'
        content += self.gen_java_class(struct)
        content += self.gen_static_data(struct)
        content += self.gen_parse_method(struct)
        content += self.gen_load_method(struct)
        content += self.gen_get_method(struct)
        content += self.gen_range_method(struct)
        content += '}\n'
        return content

    #
    def run(self, descriptors, params):
        mgr_content = '// This file is auto-generated by taxi v%s, DO NOT EDIT!\n\n' % version.VER_STRING
        mgr_filename = '%s.java' % strutil.config_manager_name

        basedir = params.get(predef.OptionOutSourceFile, '.')
        print(basedir)
        if 'pkg' in params:
            package = params['pkg']
            names = [basedir] + package.split('.')
            basedir = '/'.join(names)
            mgr_content += 'package %s;' % package
            mgr_filename = '%s/%s' % (basedir, mgr_filename)
            try:
                print('make dir', basedir)
                os.makedirs(basedir)
            except Exception as e:
                # print(e)
                pass

        class_dict = {}
        mgr_content += JAVA_CLASS_TEMPLATE % strutil.config_manager_name
        load_func_content = '    public static void loadAllConfig() {\n'

        for struct in descriptors:
            genutil.setup_comment(struct)
            genutil.setup_key_value_mode(struct)

        for struct in descriptors:
            content = '// This file is auto-generated by TAKSi v%s, DO NOT EDIT!\n\n' % version.VER_STRING
            filename = '%s.java' % struct['camel_case_name']
            # print(filename)
            if 'pkg' in params:
                filename = '%s/%s' % (basedir, filename)
                content += 'package %s;\n\n' % params['pkg']
            content += 'import java.util.*;\n'
            content += '\n'
            content += self.generate_class(struct, params)
            class_dict[filename] = content

            name = strutil.camel_to_snake(struct['name'])
            load_func_content += '        %s.loadFromFile("%s.csv");\n' % (struct['name'], name)

        load_func_content += '    }\n'
        mgr_content += load_func_content
        mgr_content += '}\n'
        class_dict[mgr_filename] = mgr_content

        for filename in class_dict:
            content = class_dict[filename]
            filename = os.path.abspath(filename)
            strutil.compare_and_save_content(filename, content, 'utf-8')
            print('wrote source file to', filename)
