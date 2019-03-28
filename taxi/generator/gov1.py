# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import codecs
import taxi.descriptor.types as types
import taxi.descriptor.predef as predef
import taxi.descriptor.lang as lang
import taxi.generator.genutil as genutil
import taxi.descriptor.strutil as strutil
import taxi.version as version

# Go code generator
class GoV1Generator():
    TAB_SPACE = '\t'

    def __init__(self):
        pass

    @staticmethod
    def name():
        return "go-v1"


    def get_const_key_name(self, name):
        return 'Key%sName' % name


    def gen_const_names(self, descriptors):
        content = 'const (\n'
        for struct in descriptors:
            content += '\t%s = "%s"\n' % (self.get_const_key_name(struct['name']), struct['name'].lower())
        content += ')\n\n'
        return content


    # 生成赋值方法
    def gen_field_assgin_stmt(self, name, typename, valuetext, tabs, tips):
        content = ''
        space = self.TAB_SPACE * tabs
        if typename == 'string':
            return '%s%s = %s\n' % (space, name, valuetext)
        else:
            content += '%svar value = MustParseTextValue("%s", %s, %s)\n' % (space, typename, valuetext, tips)
            content += '%s%s = value.(%s)\n' % (space, name, typename)
        return content


    # 生成array赋值
    def gen_field_array_assign_stmt(self, prefix, typename, name, row_name, array_delim, tabs):
        assert len(array_delim) == 1
        array_delim = array_delim.strip()
        if array_delim == '\\':
            array_delim = '\\\\'

        space = self.TAB_SPACE * tabs
        content = ''
        elem_type = types.array_element_type(typename)
        elem_type = lang.map_go_type(elem_type)

        content += '%sfor _, item := range strings.Split(%s, "%s") {\n' % (space, row_name, array_delim)
        content += '%s    var value = MustParseTextValue("%s", item, %s)\n' % (space, elem_type, row_name)
        content += '%s    %s%s = append(p.%s, value.(%s))\n' % (space, prefix, name, name, elem_type)
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
        k, v = types.map_key_value_types(typename)
        key_type = lang.map_go_type(k)
        val_type = lang.map_go_type(v)

        content = ''
        content += '%s%s%s = map[%s]%s{}\n' % (space, prefix, name, key_type, val_type)
        content += '%sfor _, text := range strings.Split(%s, "%s") {\n' % (space, row_name, delim1)
        content += '%s    if text == "" {\n' % space
        content += '%s        continue\n' % space
        content += '%s    }\n' % space
        content += '%s    var items = strings.Split(text, "%s")\n' % (space, delim2)
        content += '%s    var value = MustParseTextValue("%s", items[0], %s)\n' % (space, key_type, row_name)
        content += '%s    var key = value.(%s)\n' % (space, key_type)
        content += '%s    value = MustParseTextValue("%s", items[1], %s)\n' % (space, val_type, row_name)
        content += '%s    var val = value.(%s)\n' % (space, val_type)
        content += '%s    %s%s[key] = val\n' % (space, prefix, name)
        content += '%s}\n' % space
        return content

    #生成struct定义
    def gen_go_struct(self, struct):
        content = ''
        fields = struct['fields']
        if struct['options'][predef.PredefParseKVMode]:
            fields = genutil.get_struct_kv_fields(struct)

        inner_class_done = False
        inner_typename = ''
        inner_var_name = ''
        inner_field_names, inner_fields = genutil.get_inner_class_fields(struct)
        if len(inner_fields) > 0:
            content += self.gen_go_inner_struct(struct, inner_fields)
            inner_type_class = struct["options"][predef.PredefInnerTypeClass]
            inner_var_name = struct["options"][predef.PredefInnerTypeName]
            inner_typename = '[]%s' % inner_type_class

        vec_done = False
        vec_names, vec_name = genutil.get_vec_field_range(struct)

        content += '// %s, %s\n' % (struct['comment'], struct['file'])
        content += 'type %s struct\n{\n' % struct['camel_case_name']
        for field in fields:
            field_name = field['name']
            if field_name in inner_field_names:
                if not inner_class_done:
                    content += '    %s %s; //\n' % (inner_var_name, inner_typename)
                    inner_class_done = True
            else:
                typename = lang.map_go_type(field['original_type_name'])
                assert typename != "", field['original_type_name']

                if field_name not in vec_names:
                    content += '    %s %s // %s\n' % (field['camel_case_name'], typename, field['comment'])
                elif not vec_done:
                    vec_done = True
                    content += '    %s [%d]%s // %s\n' % (vec_name, len(vec_names), typename, field['comment'])

        return content

    # 内部class生成
    def gen_go_inner_struct(self, struct, inner_fields):
        content = ''
        class_name = struct["options"][predef.PredefInnerTypeClass]
        content += 'type %s struct {\n' % class_name
        for field in inner_fields:
            typename = lang.map_go_type(field['original_type_name'])
            assert typename != "", field['original_type_name']
            content += '    %s %s // %s\n' % (field['camel_case_name'], typename, field['comment'])
        content += '};\n\n'

        return content

    # KV模式的ParseFromRow方法
    def gen_kv_parse_method(self, struct):
        content = ''
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
                content += self.gen_field_array_assign_stmt('p.', origin_typename, name, valuetext, array_delim, 2)
            elif origin_typename.startswith('map'):
                content += self.gen_field_map_assign_stmt('p.', origin_typename, name, valuetext, map_delims, 2)
            else:
                content += self.gen_field_assgin_stmt('p.'+name, typename, valuetext, 2, idx)
            content += '%s}\n' % self.TAB_SPACE
            idx += 1
        content += '%sreturn nil\n' % self.TAB_SPACE
        content += '}\n\n'
        return content


    #生成ParseFromRow方法
    def gen_parse_method(self, struct):
        if struct['options'][predef.PredefParseKVMode]:
            return self.gen_kv_parse_method(struct)

        array_delim = struct['options'].get(predef.OptionArrayDelimeter, predef.DefaultArrayDelimiter)
        map_delims = struct['options'].get(predef.OptionMapDelimeters, predef.DefaultMapDelimiters)

        inner_class_done = False
        inner_field_names, inner_fields = genutil.get_inner_class_fields(struct)

        vec_idx = 0
        vec_names, vec_name = genutil.get_vec_field_range(struct)

        content = ''
        content += 'func (p *%s) ParseFromRow(row []string) error {\n' % struct['camel_case_name']
        content += '\tif len(row) < %d {\n' % len(struct['fields'])
        content += '\t\tlog.Panicf("%s: row length out of index %%d", len(row))\n' % struct['name']
        content += '\t}\n'

        idx = 0
        for field in struct['fields']:
            fname = field['name']
            prefix = 'p.'
            if fname in inner_field_names:
                if not inner_class_done:
                    inner_class_done = True
                    content += self.gen_inner_class_parse(struct, prefix, inner_fields)
            else:
                content += '\tif row[%d] != "" {\n' % idx
                origin_type_name = field['original_type_name']
                typename = lang.map_go_type(origin_type_name)
                field_name = field['camel_case_name']
                valuetext = 'row[%d]' % idx
                if origin_type_name.startswith('array'):
                    content += self.gen_field_array_assign_stmt(prefix, field['original_type_name'], fname, valuetext, array_delim, 2)
                elif origin_type_name.startswith('map'):
                    content += self.gen_field_map_assign_stmt(prefix, field['original_type_name'], fname, valuetext, map_delims, 2)
                else:
                    if field_name in vec_names:
                        name = '%s[%d]' % (vec_name, vec_idx)
                        content += self.gen_field_assgin_stmt(prefix+name, typename, valuetext, 2, 'row')
                        vec_idx += 1
                    else:
                        content += self.gen_field_assgin_stmt(prefix+field_name, typename, valuetext, 2, 'row')
                content += '%s}\n' % self.TAB_SPACE
            idx += 1
        content += '%sreturn nil\n' % self.TAB_SPACE
        content += '}\n\n'
        return content

    # 生成内部class的赋值方法
    def gen_inner_class_parse(self, struct, prefix, inner_fields):
        content = ''
        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        inner_var_name = struct["options"][predef.PredefInnerTypeName]
        start, end, step = genutil.get_inner_class_range(struct)
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
            content += self.gen_field_assgin_stmt('item.' + field_name, typename, valuetext, 2, 'row')
            content += '        }\n'
        content += '        %s%s = append(%s%s, item);\n' % (prefix, inner_var_name, prefix, inner_var_name)
        content += '    }\n'
        return content


    # KV模式下的Load方法
    def gen_load_method_kv(self, struct):
        content = ''
        content += 'func Load%s(loader DataSourceLoader) (*%s, error) {\n' % (struct['name'], struct['name'])
        content += '\tbuf, err := loader.LoadDataByKey(%s)\n' % self.get_const_key_name(struct['name'])
        content += '\tif err != nil {\n'
        content += '\treturn nil, err\n'
        content += '\t}\n'
        content += '\tr := csv.NewReader(buf)\n'
        content += '\trows, err := r.ReadAll()\n'
        content += '\tif err != nil {\n'
        content += '\t    log.Errorf("%s: csv read all, %%v", err)\n' % struct['name']
        content += '\t    return nil, err\n'
        content += '\t}\n'
        content += '\tvar item %s\n' % struct['name']
        content += '\tif err := item.ParseFromRows(rows); err != nil {\n'
        content += '\t    log.Errorf("%s: parse row %%d, %%v", len(rows), err)\n' % struct['name']
        content += '\t    return nil, err\n'
        content += '\t}\n'
        content += '\treturn &item, nil\n'
        content += '}\n\n'
        return content


    # 生成Load方法
    def gen_load_method(self, struct):
        content = ''
        if struct['options']['parse-kv-mode']:
            return self.gen_load_method_kv(struct)

        content += 'func Load%sList(loader DataSourceLoader) ([]*%s, error) {\n' % (struct['name'], struct['name'])
        content += '\tbuf, err := loader.LoadDataByKey(%s)\n' % self.get_const_key_name(struct['name'])
        content += '\tif err != nil {\n'
        content += '\t    return nil, err\n'
        content += '\t}\n'
        content += '\tvar list []*%s\n' % struct['name']
        content += '\tvar r = csv.NewReader(buf)\n'
        content += '\tfor i := 0; ; i++ {\n'
        content += '\t    row, err := r.Read()\n'
        content += '\t    if err == io.EOF {\n'
        content += '\t        break\n'
        content += '\t    }\n'
        content += '\t    if err != nil {\n'
        content += '\t        log.Errorf("%s: read csv %%v", err)\n' % struct['name']
        content += '\t        return nil, err\n'
        content += '\t    }\n'
        content += '\t    var item %s\n' % struct['name']
        content += '\t    if err := item.ParseFromRow(row); err != nil {\n'
        content += '\t        log.Errorf("%s: parse row %%d, %%s, %%v", i+1, row, err)\n' % struct['name']
        content += '\t        return nil, err\n'
        content += '\t    }\n'
        content += '\t    list = append(list, &item)\n'
        content += '\t}\n'
        content += '\treturn list, nil\n'
        content += '}\n\n'
        return content


    def generate(self, struct):
        content = ''
        content += self.gen_go_struct(struct)
        content += '}\n\n'
        content += self.gen_parse_method(struct)
        content += self.gen_load_method(struct)
        return content


    def run(self, descriptors, args):
        params = strutil.parse_args(args)
        content = '// This file is auto-generated by taxi v%s, DO NOT EDIT!\n\n' % version.VER_STRING
        content += 'package %s\n' % params['pkg']
        content += 'import (\n'
        content += '    "encoding/csv"\n'
        content += '    "io"\n'
        content += '    "strings"\n'
        content += ')\n'
        content += self.gen_const_names(descriptors)

        data_only = params.get(predef.OptionDataOnly, False)
        no_data = params.get(predef.OptionNoData, False)

        for struct in descriptors:
            print(strutil.current_time(), 'start generate', struct['source'])
            genutil.setup_comment(struct)
            genutil.setup_key_value_mode(struct)
            if not data_only:
                content += self.generate(struct)

        if not data_only:
            filename = params.get(predef.OptionOutSourceFile, 'config.go')
            filename = os.path.abspath(filename)
            f = codecs.open(filename, 'w', 'utf-8')
            f.writelines(content)
            f.close()
            print('wrote source to %s' % filename)

            gopath = os.getenv('GOPATH')
            if gopath is not None:
                cmd = gopath + '/bin/goimports -w ' + filename
                print(cmd)
                os.system(cmd)

        if data_only or not no_data:
            for struct in descriptors:
                genutil.write_data_rows(struct, params)
