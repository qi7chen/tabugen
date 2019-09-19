# Copyright (C) 2019-present prototyped.cn. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import json
import codecs
import taksi.descriptor.predef as predef
import taksi.descriptor.strutil as strutil
import taksi.descriptor.types as types
import taksi.generator.genutil as genutil


class JsonDataGen:
    def __init__(self):
        pass

    @staticmethod
    def name():
        return "json"

    def parse_hiden_columns(self, struct, params):
        columns = []
        if predef.OptionHideColumns in params:
            text = struct["options"].get(predef.PredefHideColumns, "")
            text = text.strip()
            if len(text) > 0:
                columns = [int(x.strip()) for x in text.split(',')]
        return columns

    def parse_primary_value(self, typename, text):
        typename = typename.strip()
        text = text.strip()
        if typename == 'bool':
            if len(text) == 0:
                return False
            return bool(text)
        if types.is_integer_type(typename):
            if len(text) == 0:
                return 0
            return int(text)
        if types.is_floating_type(typename):
            if len(text) == 0:
                return 0.0
            return float(text)
        return text

    # 解析为数组
    def parse_to_array(self, ele_type, text, dim):
        values = []
        for item in text.split(dim):
            value = self.parse_primary_value(ele_type, item)
            values.append(value)
        return values

    # 解析为字典
    def parse_to_dict(self, ktype, vtype, text, map_delims):
        obj = {}
        assert len(map_delims) == 2
        dim1 = map_delims[0]
        dim2 = map_delims[1]
        for item in text.split(dim1):
            pair = item.split(dim2)
            assert len(pair) == 2, item
            key = self.parse_primary_value(ktype, pair[0])
            value = self.parse_primary_value(vtype, pair[1])
            obj[key] = value
        return obj

    # 解析字符串为对象
    def parse_value(self, struct, typename, text):
        array_delim = struct['options'].get(predef.OptionArrayDelimeter, predef.DefaultArrayDelimiter)
        map_delims = struct['options'].get(predef.OptionMapDelimeters, predef.DefaultMapDelimiters)
        abs_type = types.is_abstract_type(typename)
        if abs_type is None:
            return self.parse_primary_value(typename, text)

        if abs_type == 'array':
            elem_type = types.array_element_type(typename)
            return self.parse_to_array(elem_type, text, array_delim)
        elif abs_type == 'map':
            ktype, vtype = types.map_key_value_types(typename)
            return self.parse_to_dict(ktype, vtype, text, map_delims)


    def parse_kv_rows(self, struct, params):
        rows = struct["data_rows"]
        typecol = int(struct['options'][predef.PredefValueTypeColumn])
        kvlist = struct['options'][predef.PredefKeyValueColumn].split(',')
        assert len(kvlist) == 2, kvlist
        keycol = int(kvlist[0])
        valuecol = int(kvlist[1])

        obj = {}
        for row in rows:
            key = row[keycol - 1].strip()
            typename = row[typecol - 1].strip()
            valuetext = row[valuecol - 1].strip()
            # print(typename, valuetext)
            value = self.parse_value(struct, typename, valuetext)
            obj[key] = value
        return obj

    #
    def parse_row_inner_obj(self, struct, row, inner_struct_fields):
        inner_obj_list = []
        start, end, step = genutil.get_inner_class_range(struct)
        for n in range(start, end, step):
            inner_item = {}
            idx = n
            for field in inner_struct_fields:
                valuetext = row[idx]
                name = field['name']
                value = self.parse_value(struct, field['original_type_name'], valuetext)
                inner_item[name] = value
                idx += 1
            inner_obj_list.append(inner_item)
        return inner_obj_list

    #
    def parse_row(self, struct, params):
        rows = struct["data_rows"]
        fields = struct['fields']
        hiden_columns = self.parse_hiden_columns(struct, params)

        # 嵌套类
        inner_var_name = ''
        inner_fields = []
        inner_field_names, mapped_inner_fields = genutil.get_inner_class_mapped_fields(struct)
        if len(mapped_inner_fields) > 0:
            inner_var_name = struct["options"][predef.PredefInnerTypeName]
            inner_fields = genutil.get_inner_class_struct_fields(struct)

        obj_list = []
        for row in rows:
            obj = {}
            inner_class_done = False
            for field in fields:
                if field['column_index'] in hiden_columns:
                    continue
                if field['name'] in inner_field_names:
                    if not inner_class_done:
                        value = self.parse_row_inner_obj(struct, row, inner_fields)
                        obj[inner_var_name] = value
                        inner_class_done = True
                else:
                    valuetext = row[field['column_index'] - 1]
                    value = self.parse_value(struct, field['original_type_name'], valuetext)
                    name = field['name']
                    obj[name] = value
            obj_list.append(obj)
        return obj_list

    # 生成
    def generate(self, struct, params):
        if predef.PredefValueTypeColumn in struct['options']:
            return self.parse_kv_rows(struct, params)
        return self.parse_row(struct, params)

    #
    def write_file(self, struct, datadir, params, obj):
        encoding = params.get(predef.OptionDataEncoding, 'utf-8')
        filename = "%s/%s.json" % (datadir, strutil.camel_to_snake(struct['camel_case_name']))
        filename = os.path.abspath(filename)
        content = json.dumps(obj, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2)
        # print(content)
        f = codecs.open(filename, "w", encoding)
        f.write(content)
        f.close()
        print("wrote json data to", filename)

    def run(self, descriptors, args):
        datadir = args.get(predef.OptionOutDataDir, '.')
        if datadir != '.':
            try:
                print('make dir', datadir)
                os.makedirs(datadir)
            except Exception as e:
                pass

        for struct in descriptors:
            obj = self.generate(struct, args)
            self.write_file(struct, datadir, args, obj)
