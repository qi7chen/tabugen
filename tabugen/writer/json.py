# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import json
from argparse import Namespace
import tabugen.predef as predef
import tabugen.typedef as types
import tabugen.util.helper as helper
import tabugen.util.tableutil as tableutil
from tabugen.structs import Struct

# 写入json文件
class JsonDataWriter:
    def __init__(self):
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
    def parse_to_dict(self, ktype: str, vtype: str, text: str):
        obj = {}
        for item in text.split(helper.Delim1):
            pair = item.split(helper.Delim2)
            assert len(pair) == 2, item
            key = self.parse_primary_value(ktype, pair[0])
            value = self.parse_primary_value(vtype, pair[1])
            obj[key] = value
        return obj

    # 解析字符串为对象
    def parse_value(self, typename: str, text: str):
        abs_type = types.is_composite_type(typename)
        if abs_type == '':
            return self.parse_primary_value(typename, text)

        if abs_type == 'array':
            elem_type = types.array_element_type(typename)
            return self.parse_to_array(elem_type, text, helper.Delim1)
        elif abs_type == 'map':
            ktype, vtype = types.map_key_value_types(typename)
            return self.parse_to_dict(ktype, vtype, text)

    def parse_kv_table(self, struct: Struct):
        rows = struct.data_rows
        obj = {}
        keyidx = struct.get_column_index(predef.PredefKVKeyName)
        typeidx = struct.get_column_index(predef.PredefKVTypeName)
        valueidx = struct.get_column_index(predef.PredefKVValueName)
        for row in rows:
            key = row[keyidx].strip()
            typename = row[typeidx].strip()
            valuetext = row[valueidx].strip()
            # print(typename, valuetext)
            value = self.parse_value(typename, valuetext)
            if self.use_snake_case:
                key = helper.camel_to_snake(key)
            obj[key] = value
        return obj

    def parse_row_to_dict(self, struct: Struct, row: list[str]):
        obj = {}
        for field in struct.fields:
            valuetext = row[field.column]
            value = self.parse_value(field.origin_type_name, valuetext)
            if self.use_snake_case:
                name = helper.camel_to_snake(field.camel_case_name)
            else:
                name = field.name
            obj[name] = value

        for array in struct.array_fields:
            array_name = array.field_name
            array_obj = []
            for field in array.element_fields:
                valuetext = row[field.column]
                value = self.parse_value(field.origin_type_name, valuetext)
                array_obj.append(value)
            obj[array_name] = array_obj
        return obj

    # 解析数据行
    def parse_table(self, struct: Struct):
        rows = struct.data_rows
        rows = tableutil.validate_unique_column(struct, rows)

        dict_list = []
        for row in rows:
            d = self.parse_row_to_dict(struct, row)
            dict_list.append(d)
        return dict_list

    # 生成
    def generate(self, struct: Struct, args: Namespace):
        if struct.options[predef.PredefParseKVMode]:
            return self.parse_kv_table(struct)
        return self.parse_table(struct)

    # 写入JSON文件
    def write_file(self, struct: Struct, filepath: str, encoding: str, json_indent: bool, obj: dict):
        filename = "%s/%s.json" % (filepath, helper.camel_to_snake(struct.camel_case_name))
        filename = os.path.abspath(filename)
        if json_indent:
            content = json.dumps(obj, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2)
        else:
            content = json.dumps(obj, ensure_ascii=False, allow_nan=False, sort_keys=True)

        if helper.save_content_if_not_same(filename, content, encoding):
            print("wrote JSON data to", filename)

    def process(self, descriptors: list[Struct], args: Namespace):
        filepath = args.out_data_path
        encoding = args.data_file_encoding

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
