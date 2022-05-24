# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import json
import codecs
import tabugen.predef as predef
import tabugen.typedef as types
import tabugen.util.strutil as strutil
import tabugen.util.structutil as structutil
import tabugen.util.rowutil as rowutil


# 写入json文件
class JsonDataWriter:
    def __init__(self):
        self.array_delim = '|'
        self.map_delims = ['|', '=']
        self.use_snake_case = False

    @staticmethod
    def name():
        return "json"

    @staticmethod
    def parse_primary_value(typename: str, text: str):
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
    def parse_value(self, typename, text):
        abs_type = types.is_abstract_type(typename)
        if abs_type == '':
            return self.parse_primary_value(typename, text)

        if abs_type == 'array':
            elem_type = types.array_element_type(typename)
            return self.parse_to_array(elem_type, text, self.array_delim)
        elif abs_type == 'map':
            ktype, vtype = types.map_key_value_types(typename)
            return self.parse_to_dict(ktype, vtype, text, self.map_delims)

    def parse_kv_rows(self, struct, params):
        rows = struct["data_rows"]
        typecol = int(struct['options'][predef.PredefValueTypeColumn])
        kvlist = struct['options'][predef.PredefKeyValueColumns].split(',')
        assert len(kvlist) >= 3, kvlist
        keycol = int(kvlist[0])
        valuecol = int(kvlist[2])

        obj = {}
        for row in rows:
            key = row[keycol - 1].strip()
            typename = row[typecol - 1].strip()
            valuetext = row[valuecol - 1].strip()
            # print(typename, valuetext)
            value = self.parse_value(typename, valuetext)
            if self.use_snake_case:
                key = strutil.camel_to_snake(key)
            obj[key] = value
        return obj

    #
    def parse_row_inner_obj(self, struct, row, inner_struct_fields):
        inner_obj_list = []
        start, end, step = structutil.get_inner_class_range(struct)
        for n in range(start, end, step):
            inner_item = {}
            idx = n
            for field in inner_struct_fields:
                valuetext = row[idx]
                name = field['name']
                value = self.parse_value(field['original_type_name'], valuetext)
                if self.use_snake_case:
                    name = strutil.camel_to_snake(name)
                inner_item[name] = value
                idx += 1
            inner_obj_list.append(inner_item)
        return inner_obj_list


    def row_to_object(self, struct, row, fields, inner_field_names, inner_var_name, inner_fields):
        obj = {}
        inner_class_done = False
        idx = 0
        for field in fields:
            if not field['enable']:
                continue
            if field['name'] in inner_field_names:
                if not inner_class_done:
                    value = self.parse_row_inner_obj(struct, row, inner_fields)
                    if self.use_snake_case:
                        inner_var_name = strutil.camel_to_snake(inner_var_name)
                    obj[inner_var_name] = value
                    inner_class_done = True
            else:
                valuetext = row[idx]
                value = self.parse_value(field['original_type_name'], valuetext)
                if self.use_snake_case:
                    name = strutil.camel_to_snake(field['camel_case_name'])
                else:
                    name = field['name']
                obj[name] = value
            idx += 1
        return obj


    # 解析数据行
    def parse_row(self, struct):
        rows = struct["data_rows"]
        rows = rowutil.validate_unique_column(struct, rows)
        rows = rowutil.hide_skipped_row_fields(struct, rows)

        fields = structutil.enabled_fields(struct)

        # 嵌套类
        inner_var_name = ''
        inner_fields = []
        inner_field_names, mapped_inner_fields = structutil.get_inner_class_mapped_fields(struct)
        if len(mapped_inner_fields) > 0:
            inner_var_name = struct["options"][predef.PredefInnerTypeName]
            inner_fields = structutil.get_inner_class_struct_fields(struct)

        obj_list = []
        for row in rows:
            obj = self.row_to_object(struct, row, fields, inner_field_names, inner_var_name, inner_fields)
            obj_list.append(obj)
        return obj_list

    # 生成
    def generate(self, struct, args):
        if predef.PredefValueTypeColumn in struct['options']:
            return self.parse_kv_rows(struct, args)
        return self.parse_row(struct)

    # 写入JSON文件
    def write_file(self, struct, filepath, encoding, json_indent, obj):
        filename = "%s/%s.json" % (filepath, strutil.camel_to_snake(struct['camel_case_name']))
        filename = os.path.abspath(filename)
        if json_indent:
            content = json.dumps(obj, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2)
        else:
            content = json.dumps(obj, ensure_ascii=False, allow_nan=False, sort_keys=True)

        if strutil.save_content_if_not_same(filename, content, encoding):
            print("wrote JSON data to", filename)

    def process(self, descriptors, args):
        filepath = args.out_data_path
        encoding = args.data_file_encoding
        (self.array_delim, self.map_delims) = strutil.to_sep_delimiters(args.array_delim, args.map_delims)

        if filepath != '.':
            try:
                # print('make dir', filepath)
                os.makedirs(filepath)
            except OSError as e:
                pass

        if args.json_snake_case:
            self.use_snake_case = True
        for struct in descriptors:
            obj = self.generate(struct, args)
            self.write_file(struct, filepath, encoding, args.json_indent, obj)
