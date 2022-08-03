# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import json
import tabugen.predef as predef
import tabugen.typedef as types
import tabugen.util.strutil as strutil
import tabugen.util.tableutil as tableutil


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
    def parse_to_dict(self, ktype, vtype, text):
        obj = {}
        for item in text.split(predef.PredefDelim1):
            pair = item.split(predef.PredefDelim2)
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
            return self.parse_to_array(elem_type, text, predef.PredefDelim1)
        elif abs_type == 'map':
            ktype, vtype = types.map_key_value_types(typename)
            return self.parse_to_dict(ktype, vtype, text)

    def parse_kv_rows(self, struct, params):
        rows = struct["data_rows"]
        obj = {}
        for row in rows:
            key = row[predef.PredefKeyColumn].strip()
            typename = row[predef.PredefValueTypeColumn].strip()
            valuetext = row[predef.PredefValueColumn].strip()
            # print(typename, valuetext)
            value = self.parse_value(typename, valuetext)
            if self.use_snake_case:
                key = strutil.camel_to_snake(key)
            obj[key] = value
        return obj

    #
    def parse_row_inner_obj(self, struct, row, inner_fields):
        obj_list = []
        start = inner_fields['start']
        end = inner_fields['end']
        step = inner_fields['step']

        while start < end:
            obj = {}
            for n in range(step):
                col = start + n
                field = struct['fields'][col]
                valuetext = row[col]
                name = strutil.remove_suffix_number(field['name'])
                value = self.parse_value(field['original_type_name'], valuetext)
                if self.use_snake_case:
                    name = strutil.camel_to_snake(name)
                obj[name] = value
            obj_list.append(obj)
            start += step
        return obj_list

    def row_to_object(self, struct, row, inner_fields):
        obj = {}
        inner_class_done = False
        for col, field in enumerate(struct['fields']):
            if inner_fields['start'] <= col <  inner_fields['end']:
                if not inner_class_done:
                    inner_class_done = True
                    inner_var_name = struct['options'][predef.PredefInnerFieldName]
                    value = self.parse_row_inner_obj(struct, row, inner_fields)
                    obj[inner_var_name] = value
            else:
                valuetext = row[col]
                value = self.parse_value(field['original_type_name'], valuetext)
                if self.use_snake_case:
                    name = strutil.camel_to_snake(field['camel_case_name'])
                else:
                    name = field['name']
                obj[name] = value
        return obj

    # 解析数据行
    def parse_row(self, struct):
        rows = struct["data_rows"]
        rows = tableutil.validate_unique_column(struct, rows)

        # 嵌套类
        inner_fields = {'start': -1, 'end': -1, 'step': 0}
        if 'inner_fields' in struct:
            inner_fields['start'] = struct['inner_fields']['start']
            inner_fields['end'] = struct['inner_fields']['end']
            inner_fields['step'] = struct['inner_fields']['step']

        obj_list = []
        for row in rows:
            obj = self.row_to_object(struct, row, inner_fields)
            obj_list.append(obj)
        return obj_list

    # 生成
    def generate(self, struct, args):
        if struct['options'][predef.PredefParseKVMode]:
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
