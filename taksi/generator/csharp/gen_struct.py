# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import taksi.predef as predef
import taksi.lang as lang
import taksi.strutil as strutil
import taksi.generator.genutil as genutil
import taksi.version as version
from taksi.generator.csharp.gen_csv_load import CSharpCsvLoadGenerator
from taksi.generator.csharp.gen_json_load import CSharpJsonLoadGenerator


CSHARP_METHOD_TEMPLATE = """
    public delegate void ContentReader(string filepath, Action<string> cb);
    
    public static ContentReader reader = ReadFileContent;
    
    public static bool ParseBool(string text)
    {
        if (text.Length > 0)
        {
            return string.Equals(text, "1") ||
                string.Equals(text, "on", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(text, "yes", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(text, "true", StringComparison.OrdinalIgnoreCase);
        }
        return false;
    }
        
    public static List<string> ReadTextToLines(string content)
    {
        List<string> lines = new List<string>();
        using (StringReader reader = new StringReader(content))
        {
            string line;
            while ((line = reader.ReadLine()) != null)
            {
                lines.Add(line);
            }
        }
        return lines;
    }
    
    public static void ReadFileContent(string filepath, Action<string> cb)
    {
        StreamReader reader = new StreamReader(filepath);
        var content = reader.ReadToEnd();
        cb(content);
    }
    
"""


# C#代码生成器
class CSharpStructGenerator:
    TAB_SPACE = '    '

    def __init__(self):
        self.load_gen = None

    def init(self, loader_name):
        """
            :param loader_name: loader需要满足2个接口
                gen_struct_method_declare()
                gen_source_content()
        """
        if loader_name is not None:
            if loader_name.strip() == "csv":
                self.load_gen = CSharpCsvLoadGenerator()
            elif loader_name.strip() == "json":
                pass

    @staticmethod
    def name():
        return "csharp"

    # 生成结构体定义
    def gen_cs_struct(self, struct):
        content = ''

        fields = struct['fields']
        if struct['options'][predef.PredefParseKVMode]:
            fields = genutil.get_struct_kv_fields(struct)

        inner_class_done = False
        inner_typename = ''
        inner_var_name = ''
        inner_field_names, inner_fields = genutil.get_inner_class_mapped_fields(struct)
        if len(inner_fields) > 0:
            content += self.gen_cs_inner_class(struct)
            inner_type_class = struct["options"][predef.PredefInnerTypeClass]
            inner_var_name = struct["options"][predef.PredefInnerTypeName]
            inner_typename = '%s[]' % inner_type_class

        content += '// %s, %s\n' % (struct['comment'], struct['file'])
        content += 'public class %s\n{\n' % struct['name']

        vec_done = False
        vec_names, vec_name = genutil.get_vec_field_range(struct)

        max_name_len = strutil.max_field_length(fields, 'name', None)
        max_type_len = strutil.max_field_length(fields, 'original_type_name', lang.map_cs_type)
        if len(inner_typename) > max_type_len:
            max_type_len = len(inner_typename)

        for field in fields:
            field_name = field['name']
            if field_name in inner_field_names:
                if not inner_class_done:
                    typename = strutil.pad_spaces(inner_typename, max_type_len)
                    content += '    public %s %s = null; \n' % (typename, inner_var_name)
                    inner_class_done = True
            else:
                typename = lang.map_cs_type(field['original_type_name'])
                assert typename != "", field['original_type_name']
                typename = strutil.pad_spaces(typename, max_type_len + 1)
                if field['name'] not in vec_names:
                    name = lang.name_with_default_cs_value(field, typename)
                    name = strutil.pad_spaces(name, max_name_len + 8)
                    content += '    public %s %s // %s\n' % (typename, name, field['comment'])
                elif not vec_done:
                    name = '%s = new %s[%d];' % (vec_name, typename.strip(), len(vec_names))
                    name = strutil.pad_spaces(name, max_name_len + 8)
                    content += '    public %s[] %s // %s\n' % (typename.strip(), name, field['comment'])
                    vec_done = True

        return content

    #
    def gen_cs_inner_class(self, struct):
        content = ''
        class_name = struct["options"][predef.PredefInnerTypeClass]
        inner_fields = genutil.get_inner_class_struct_fields(struct)
        content += 'public class %s \n' % class_name
        content += '{\n'
        max_name_len = strutil.max_field_length(inner_fields, 'name', None)
        max_type_len = strutil.max_field_length(inner_fields, 'original_type_name', lang.map_cs_type)
        for field in inner_fields:
            typename = lang.map_cs_type(field['original_type_name'])
            assert typename != "", field['original_type_name']
            typename = strutil.pad_spaces(typename, max_type_len + 1)
            name = lang.name_with_default_cs_value(field, typename)
            name = strutil.pad_spaces(name, max_name_len + 8)
            content += '    public %s %s // %s\n' % (typename.strip(), name, field['comment'])
        content += '};\n\n'
        return content

    def generate_class(self, struct):
        content = '\n'
        content += self.gen_cs_struct(struct)
        if self.load_gen is not None:
            content += self.load_gen.gen_source_method(struct)
        content += '}\n\n'
        return content

    def run(self, descriptors, args):
        content = '// This file is auto-generated by TAKSi v%s, DO NOT EDIT!\n\n' % version.VER_STRING
        content += 'using System;\n'
        content += 'using System.IO;\n'
        content += 'using System.Collections.Generic;\n'

        if args.package is not None:
            content += '\nnamespace %s\n{\n' % args.package

        for struct in descriptors:
            genutil.setup_comment(struct)
            genutil.setup_key_value_mode(struct)

        for struct in descriptors:
            content += self.generate_class(struct)

        if self.load_gen is not None:
            content += self.load_gen.gen_global_class(descriptors)

        if args.package is not None:
            content += '\n}\n'  # namespace

        filename = 'AutogenConfig.cs'
        if args.out_source_path is not None:
            filename = str(args.out_source_path)
        filename = os.path.abspath(filename)
        strutil.save_content_if_not_same(filename, content, 'utf-8')
        print('wrote C# source file to', filename)
