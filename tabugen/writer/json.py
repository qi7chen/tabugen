# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import json
import traceback
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
    def parse_primary_value(typename: str, text: str, args: Namespace):
        typename = typename.strip()
        text = text.strip()
        if typename == 'bool':
            if len(text) == 0:
                return False
            return bool(text)
        if types.is_integer_type(typename):
            if len(text) == 0:
                return 0
            if args.legacy:
                try:
                    return int(text)
                except ValueError:
                    return int(text, 16)  # try hex
            else:
                return int(text)

        if types.is_floating_type(typename):
            if len(text) == 0:
                return 0.0
            return float(text)
        return text

    # 解析为数组
    def parse_to_array(self, ele_type: str, text: str, dim: str, args: Namespace):
        values = []
        for item in text.split(dim):
            value = self.parse_primary_value(ele_type, item, args)
            values.append(value)
        return values

    # 解析为字典
    def parse_to_dict(self, ktype: str, vtype: str, text: str, args: Namespace):
        obj = {}
        for item in text.split(helper.Delim1):
            pair = item.split(helper.Delim2)
            assert len(pair) == 2, item
            key = self.parse_primary_value(ktype, pair[0], args)
            value = self.parse_primary_value(vtype, pair[1], args)
            obj[key] = value
        return obj

    # 解析字符串为对象
    def parse_value(self, typename: str, text: str, args: Namespace):
        abs_type = types.is_composite_type(typename)
        if abs_type == '':
            return self.parse_primary_value(typename, text, args)

        if abs_type == 'array':
            elem_type = types.array_element_type(typename)
            return self.parse_to_array(elem_type, text, helper.Delim1, args)
        elif abs_type == 'map':
            ktype, vtype = types.map_key_value_types(typename)
            return self.parse_to_dict(ktype, vtype, text, args)

    def parse_kv_table(self, struct: Struct, args: Namespace):
        rows = struct.data_rows
        obj = {}
        keyidx = struct.get_column_index(predef.PredefKVKeyName)
        typeidx = struct.get_column_index(predef.PredefKVTypeName)
        valueidx = struct.get_column_index(predef.PredefKVValueName)
        for row in rows:
            key = row[keyidx].strip()
            typename = row[typeidx].strip()
            if args.legacy:
                try:
                    typn = int(typename)
                    typename = types.legacy_type_to_name(typn)
                except ValueError:
                    pass
            valuetext = row[valueidx].strip()
            # print(typename, valuetext)
            try:
                value = self.parse_value(typename, valuetext, args)
                if self.use_snake_case:
                    key = helper.camel_to_snake(key)
                obj[key] = value
            except Exception as e:
                print(e, traceback.format_exc())

        return obj

    def parse_row_to_dict(self, struct: Struct, row: list[str], args: Namespace):
        obj = {}
        for field in struct.fields:
            valuetext = row[field.column]
            value = self.parse_value(field.origin_type_name, valuetext, args)
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
                value = self.parse_value(field.origin_type_name, valuetext, args)
                array_obj.append(value)
            obj[array_name] = array_obj
        return obj

    # 解析数据行
    def parse_table(self, struct: Struct, args: Namespace):
        rows = struct.data_rows
        rows = tableutil.validate_unique_column(struct, rows)

        dict_list = []
        for row in rows:
            d = self.parse_row_to_dict(struct, row, args)
            dict_list.append(d)
        return dict_list

    # 生成
    def generate(self, struct: Struct, args: Namespace):
        if struct.options[predef.PredefParseKVMode]:
            return self.parse_kv_table(struct, args)
        return self.parse_table(struct, args)

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
