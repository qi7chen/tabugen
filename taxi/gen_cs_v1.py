# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import codecs
import descriptor
import basegen
import predef
import util


CSharpStaticClassName = "AutogenConfigData"

METHOD_TEMPLATE = """
    public static bool ParseBoolean(string text)
    {
        text = text.Trim().ToLower();
        return text == "1" || text == "true" || text == "yes" || text == "on";
    }
    
    public static string[] ReadFileLines(string name)
    {
        string filepath = string.Format("{0}csv/{1}.csv", ResourceManager.PersistentDataPath, name);
        return File.ReadAllLines(filepath, Encoding.UTF8);
    }  
"""



# C# code generator
class CSV1Generator(basegen.CodeGeneratorBase):
    TAB_SPACE = '    '

    def __init__(self):
        pass

    @staticmethod
    def name():
        return "cs-v1"


    def get_data_member_name(self, name):
        return name + 'Data'

    # 字段比较
    def gen_equal_stmt(self, prefix, struct, key):
        keys = self.get_struct_keys(struct, key, map_cs_type)
        args = []
        for tpl in keys:
            args.append('%s%s == %s' % (prefix, tpl[1], tpl[1]))
        return ' && '.join(args)

    # 生成赋值方法
    def gen_field_assgin_stmt(self, name, typename, valuetext, tabs):
        content = ''
        space = self.TAB_SPACE * tabs
        if typename.lower() == 'string':
            content += '%s%s = %s.Trim();\n' % (space, name, valuetext)
        elif typename.lower().find('bool') >= 0:
            content += '%s%s = AutogenConfigData.ParseBoolean(%s);\n' % (space, name, valuetext)
        else:
            content += '%s%s = %s.Parse(%s);\n' % (space, name, cs_box_type(typename), valuetext)
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
        elem_type = map_cs_type(elem_type)
        content += "%sforeach(string item in %s.Split('%s')) {\n" % (space, row_name, array_delim)
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
        key_type = map_cs_type(k)
        val_type = map_cs_type(v)

        content = ''
        content += "%sforeach(string text in %s.Split('%s')) {\n" % (space, row_name, delim1)
        content += '%s    if (text == "") {\n' % space
        content += '%s        continue;\n' % space
        content += '%s    }\n' % space
        content += "%s    var item = text.Split('%s');\n" % (space, delim2)
        content += self.gen_field_assgin_stmt('var key', key_type, 'item[0]', tabs+1)
        content += self.gen_field_assgin_stmt('var value', val_type, 'item[1]', tabs + 1)
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
        content += '%spublic static %s ParseFromRows(List<List<string>> rows) {\n' % (self.TAB_SPACE, struct['camel_case_name'])
        content += '%sif (rows.Count < %d) {\n' % (self.TAB_SPACE*2, len(rows))
        content += '%sthrow new ArgumentException(string.Format("%s: row length out of index, {0} < %d", rows.Count));\n' % (self.TAB_SPACE*3, struct['name'], len(rows))
        content += '%s}\n' % (self.TAB_SPACE*2)
        content += '%s%s obj = new %s();\n' % (self.TAB_SPACE * 2, struct['camel_case_name'], struct['camel_case_name'])

        idx = 0
        for row in rows:
            content += '%sif (rows[%d][%d] != "") {\n' % (self.TAB_SPACE*2, idx, validx)
            name = rows[idx][keyidx].strip()
            name = util.camel_case(name)
            origin_typename = rows[idx][typeidx].strip()
            typename = map_cs_type(origin_typename)
            valuetext = 'rows[%d][%d]' % (idx, validx)
            # print('kv', name, origin_typename, valuetext)
            if origin_typename.startswith('array'):
                content += self.gen_field_array_assign_stmt('obj.', origin_typename, name, valuetext, array_delim, 3)
            elif origin_typename.startswith('map'):
                content += self.gen_field_map_assign_stmt('obj.', origin_typename, name, valuetext, map_delims, 3)
            else:
                content += self.gen_field_assgin_stmt('obj.' + name, typename, valuetext, 3)
            content += '%s}\n' % (self.TAB_SPACE*2)
            idx += 1
        content += '%sreturn obj;\n' % (self.TAB_SPACE*2)
        content += '%s}\n\n' % self.TAB_SPACE
        return content


    # 生成ParseFromRow方法
    def gen_parse_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct)

        array_delim = struct['options'].get(predef.OptionArrayDelimeter, predef.DefaultArrayDelimiter)
        map_delims = struct['options'].get(predef.OptionMapDelimeters, predef.DefaultMapDelimiters)

        vec_idx = 0
        vec_names, vec_name = self.get_field_range(struct)

        content = ''
        content += '%s// parse data object from an csv row\n' % self.TAB_SPACE
        content += '%spublic static %s ParseFromRow(IList<string> row) {\n' % (self.TAB_SPACE, struct['camel_case_name'])
        content += '%sif (row.Count < %d) {\n' % (self.TAB_SPACE*2, len(struct['fields']))
        content += '%sthrow new ArgumentException(string.Format("%s: row length out of index {0}", row.Count));\n' % (self.TAB_SPACE * 3, struct['name'])
        content += '%s}\n' % (self.TAB_SPACE*2)
        content += '%s%s obj = new %s();\n' % (self.TAB_SPACE * 2, struct['camel_case_name'], struct['camel_case_name'])

        idx = 0
        for field in struct['fields']:
            content += '%sif (row[%d] != "") {\n' % (self.TAB_SPACE*2, idx)
            origin_type_name = field['original_type_name']
            typename = map_cs_type(origin_type_name)
            field_name = field['name']
            valuetext = 'row[%d]' % idx
            if origin_type_name.startswith('array'):
                content += self.gen_field_array_assign_stmt('obj.', field['original_type_name'], field['name'], valuetext, array_delim, 3)
            elif origin_type_name.startswith('map'):
                content += self.gen_field_map_assign_stmt('obj.', field['original_type_name'], field['name'], valuetext, map_delims, 3)
            else:
                if field_name in vec_names:
                    name = '%s[%d]' % (vec_name, vec_idx)
                    content += self.gen_field_assgin_stmt('obj.'+name, typename, valuetext, 3)
                    vec_idx += 1
                else:
                    content += self.gen_field_assgin_stmt('obj.'+field_name, typename, valuetext, 3)
            content += '%s}\n' % (self.TAB_SPACE*2)
            idx += 1
        content += '%sreturn obj;\n' % (self.TAB_SPACE*2)
        content += '%s}\n\n' % self.TAB_SPACE
        return content


    # 生成结构体定义
    def gen_cs_struct(self, struct):
        fields = struct['fields']
        if struct['options'][predef.PredefParseKVMode]:
            fields = self.get_struct_kv_fields(struct)

        vec_done = False
        vec_names, vec_name = self.get_field_range(struct)

        max_name_len = util.max_field_length(fields, 'name', None)
        max_type_len = util.max_field_length(fields, 'original_type_name', map_cs_type)

        content = '// %s\n' % struct['comment']
        content += 'public class %s\n{\n' % struct['name']
        for field in fields:
            typename = map_cs_type(field['original_type_name'])
            assert typename != "", field['original_type_name']
            typename = util.pad_spaces(typename, max_type_len + 1)
            if field['name'] not in vec_names:
                name = name_with_default_value(field, typename)
                name = util.pad_spaces(name, max_name_len + 8)
                content += '    public %s %s // %s\n' % (typename, name, field['comment'])
            elif not vec_done:
                name = '%s = new %s[%d];' % (vec_name, typename.strip(), len(vec_names))
                name = util.pad_spaces(name, max_name_len + 8)
                content += '    public %s[] %s // %s\n' % (typename.strip(), name, field['comment'])
                vec_done = True

        return content


    def gen_static_data(self, struct):
        content = '\n'
        if struct['options'][predef.PredefParseKVMode]:
            content += '    private static %s data_ = new %s(); // %s\n\n' % (struct['name'], struct['name'], struct['comment'])
            content += '    public static %s GetData() {\n' % struct['name']
            content += '        return data_;\n'
            content += '    }\n\n'
        else:
            content += '    private static List<%s> data_ = new List<%s>(); // %s\n\n' % (struct['name'], struct['name'], struct['comment'])
            content += '    public static List<%s> GetData() {\n' % struct['name']
            content += '        return data_;\n'
            content += '    }\n\n'

        return content


    def gen_kv_struct_load_method(self, struct):
        rows = struct['data-rows']
        keycol = struct['options'][predef.PredefKeyColumn]
        valcol = struct['options'][predef.PredefValueColumn]
        typcol = int(struct['options'][predef.PredefValueTypeColumn])
        assert keycol > 0 and valcol > 0 and typcol > 0

        keyidx, keyfield = self.get_field_by_column_index(struct, keycol)
        validx, valfield = self.get_field_by_column_index(struct, valcol)
        typeidx, typefield = self.get_field_by_column_index(struct, typcol)

        content = '%spublic static void Load() {\n' % self.TAB_SPACE
        content += '%sstring[] lines = %s.ReadFileLines(%s);\n' % (self.TAB_SPACE*2, CSharpStaticClassName, struct['name'].lower())
        content += '%svar rows = new List<List<string>>();\n' % (self.TAB_SPACE * 2)
        content += '%sforeach(string line in lines)\n' % (self.TAB_SPACE*2)
        content += '%s{\n' % (self.TAB_SPACE*2)
        content += "%sstring[] row = line.Split(',');\n" % (self.TAB_SPACE*3)
        content += '%srows.Add(row.ToList());\n' % (self.TAB_SPACE * 3)
        content += '%s}\n' % (self.TAB_SPACE*2)
        content += '%sdata_ = %s.ParseFromRows(rows);\n' % (self.TAB_SPACE * 2, struct['name'])
        content += '%s}\n\n' % self.TAB_SPACE
        return content

    # 生成Load方法
    def gen_load_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_struct_load_method(struct)

        content = ''
        content = '%spublic static void Load() {\n' % self.TAB_SPACE
        content += '%sdata_ = new List<%s>();\n' % (self.TAB_SPACE * 2, struct['name'])
        content += '%sstring[] lines = %s.ReadFileLines(%s);\n' % (self.TAB_SPACE*2, CSharpStaticClassName, struct['name'].lower())
        content += '%sforeach(string line in lines)\n' % (self.TAB_SPACE * 2)
        content += '%s{\n' % (self.TAB_SPACE * 2)
        content += "%sstring[] row = line.Split(',');\n" % (self.TAB_SPACE * 3)
        content += "%svar obj = %s.ParseFromRow(row);\n" % (self.TAB_SPACE * 3, struct['name'])
        content += "%sdata_.Add(obj);\n" % (self.TAB_SPACE * 3)
        content += '%s}\n' % (self.TAB_SPACE * 2)
        content += '%s}\n\n' % self.TAB_SPACE
        return content


    # 生成Get()方法
    def gen_get_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return ''

        keys = self.get_struct_keys(struct, predef.PredefGetMethodKeys, map_cs_type)
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
        content += '    public static %s Get(%s)\n' % (struct['name'], ', '.join(formal_param))
        content += '    {\n'
        content += '        foreach (%s item in GetData())\n' % struct['name']
        content += '        {\n'
        content += '            if (%s)\n' % self.gen_equal_stmt('item.', struct, 'get-keys')
        content += '            {\n'
        content += '                return item;\n'
        content += '            }\n'
        content += '        }\n'
        content += '        return null;\n'
        content += '    }\n\n'
        return content

    # 生成GetRange()方法
    def gen_range_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return ''

        if predef.PredefRangeMethodKeys not in struct['options']:
            return ''

        keys = self.get_struct_keys(struct, predef.PredefRangeMethodKeys, map_cs_type)
        assert len(keys) > 0

        formal_param = []
        params = []
        arg_names = []
        for tpl in keys:
            typename = tpl[0]
            formal_param.append('%s %s' % (typename, tpl[1]))
            arg_names.append(tpl[1])

        content = ''
        content += '    // get a range of items by key\n'
        content += '    public static List<%s> GetRange(%s)\n' % (struct['name'], ', '.join(formal_param))
        content += '    {\n'
        content += '        var range = new List<%s>();\n' % struct['name']
        content += '        foreach (%s item in GetData())\n' % struct['name']
        content += '        {\n'
        content += '            if (%s)\n' % self.gen_equal_stmt('item.', struct, 'range-keys')
        content += '            {\n'
        content += '                range.Add(item);\n'
        content += '            }\n'
        content += '            else \n'
        content += '            {\n'
        content += '                if (range.Count > 0) \n'
        content += '                    break;\n'
        content += '            }\n'
        content += '        }\n'
        content += '        return range;\n'
        content += '    }\n\n'
        return content


    def gen_global_class(self, descriptors):
        content = ''
        content += 'public class %s\n{\n' % CSharpStaticClassName
        content += '    public static bool LoadAll() \n'
        content += '    {\n'
        for struct in descriptors:
            content += '        %s.Load();\n' % struct['name']
        content += '        return true;\n'
        content += '    }\n'
        content += METHOD_TEMPLATE
        content += '}\n\n'
        return content


    def generate(self, struct):
        content = '\n'
        content += self.gen_cs_struct(struct)
        content += self.gen_static_data(struct)
        content += self.gen_parse_method(struct)
        content += self.gen_load_method(struct)
        content += self.gen_get_method(struct)
        content += self.gen_range_method(struct)
        content += '}\n\n'
        return content


    def run(self, descriptors, args):
        params = util.parse_args(args)
        content = '// This file is auto-generated by taxi v%s, DO NOT EDIT!\n\n' % util.version_string
        content += 'using System;\n'
        content += 'using System.IO;\n'
        content += 'using System.Text;\n'
        content += 'using System.Linq;\n'
        content += 'using System.Collections;\n'
        content += 'using System.Collections.Generic;\n'

        if 'pkg' in params:
            content += '\nnamespace %s\n{\n\n' % params['pkg']

        data_only = params.get(predef.OptionDataOnly, False)
        no_data = params.get(predef.OptionNoData, False)

        for struct in descriptors:
            print('start generate', struct['source'])
            self.setup_comment(struct)
            self.setup_key_value_mode(struct)
            if not no_data:
                self.write_data_rows(struct, params)
            if not data_only:
                content += self.generate(struct)

        content += self.gen_global_class(descriptors)

        if 'pkg' in params:
            content += '\n}\n'  # namespace

        filename = params.get(predef.OptionOutSourceFile, 'ConfigData.cs')
        filename = os.path.abspath(filename)
        f = codecs.open(filename, 'w', 'utf-8')
        f.writelines(content)
        f.close()
        print('wrote to %s' % filename)


# C#类型映射
def map_cs_type(typ):
    type_mapping = {
        'bool':     'bool',
        'int8':     'sbyte',
        'uint8':    'byte',
        'int16':    'short',
        'uint16':   'ushort',
        'int':      'int',
        'uint':     'uint',
        'int32':    'int',
        'uint32':   'uint',
        'int64':    'long',
        'uint64':   'ulong',
        'float':    'float',
        'float32':  'float',
        'float64':  'double',
        'enum':     'int',
        'string':   'string',
    }
    abs_type = descriptor.is_abstract_type(typ)
    if abs_type is None:
        return type_mapping[typ]

    if abs_type == 'array':
        t = descriptor.array_element_type(typ)
        elem_type = type_mapping[t]
        return 'List<%s>' % elem_type
    elif abs_type == 'map':
        k, v = descriptor.map_key_value_types(typ)
        key_type = type_mapping[k]
        value_type = type_mapping[v]
        return 'Dictionary<%s, %s>' % (key_type, value_type)
    assert False, typ


# 装箱类型
def cs_box_type(name):
    return name

# 默认值
def name_with_default_value(field, typename):
    typename = typename.strip()
    line = ''
    if typename == 'bool':
        line = '%s = false;' % field['name']
    elif typename == 'string':
        line = '%s = "";' % field['name']
    elif descriptor.is_integer_type(field['type_name']):
        line = '%s = 0;' % field['name']
    elif descriptor.is_floating_type(field['type_name']):
        line = '%s = 0.0f;' % field['name']
    elif typename.startswith('List'):
        line = '%s = new %s();' % (field['name'], typename)
    elif typename.startswith('Dictionary'):
        line = '%s = new %s();' % (field['name'], typename)
    else:
        line = '%s;' % field['name']
    assert len(line) > 0
    return line
