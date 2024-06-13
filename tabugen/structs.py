# Copyright (C) 2024 ki7chen@github. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import copy
from tabugen.util import helper


# 结构的字段
class StructField:

    def __init__(self):
        self.origin_name = ''  # 原始字段名
        self.name = ''  # 字段名
        self.camel_case_name = ''  # 驼峰命名
        self.origin_type_name = ''  # 原始类型名，可能是type alias
        self.type_name = ''  # 类型名
        self.type = 0  # 类型
        self.comment = ''  # 注释


class ArrayField:

    def __init__(self):
        self.name = ''
        self.camel_case_name = ''
        self.comment = ''
        self.type_name = ''
        self.field_name = ''
        self.element_fields: list[StructField] = []


# 内嵌类型字段
class EmbedField:

    def __init__(self):
        self.camel_case_name = ''
        self.comment = ''
        self.class_name = ''
        self.field_name = ''
        self.element_fields: list[StructField] = []
        self.field_names = []

    def max_length(self, type_mapper) -> (int, int):
        max_name_len = 0
        max_type_len = 0
        for field in self.element_fields:
            name_len = len(field.name)
            type_name = field.type_name
            type_len = len(type_mapper(type_name))
            if name_len > max_name_len:
                max_name_len = name_len
            if type_len > max_type_len:
                max_type_len = type_len
        return max_name_len, max_type_len

    def generate_field_name(self):
        result_name = ''
        for field in self.element_fields:
            name = helper.camel_to_snake(field.name)
            components = name.split('_')
            result_name += components[0].title()
        self.field_name = result_name
        self.class_name = 'T' + result_name


# 一个结构定义
class Struct:

    def __init__(self):
        self.name = ''
        self.raw_fields: list[StructField] = []
        self.fields: list[StructField] = []
        self.options = {}
        self.camel_case_name = ''
        self.comment = ''
        self.parse_time = 0
        self.array_fields: list[ArrayField] = []  # 内嵌数组字段
        self.embed_fields: list[EmbedField] = []  # 内嵌类型字段
        self.data_rows = []  # 数据

    def get_field_by_name(self, name: str) -> StructField | None:
        for field in self.fields:
            if field.name == name:
                return field
        return None

    # 获取字段名最大长度
    def max_field_name_length(self):
        max_len = 0
        for field in self.fields:
            n = len(field.name)
            if n > max_len:
                max_len = n
        for embed in self.embed_fields:
            n = len(embed.field_name)
            if n > max_len:
                max_len = n
        return max_len

    # 获取字段类型最大长度
    def max_field_type_length(self, mapper=None):
        max_len = 0
        for field in self.fields:
            n = len(field.origin_type_name)
            if mapper is not None:
                n = len(mapper(field.origin_type_name))
            if n > max_len:
                max_len = n
        for embed in self.embed_fields:
            n = len(embed.class_name)
            if n > max_len:
                max_len = n
        return max_len

    def remove_field_by_name(self, name: str):
        for i, field in enumerate(self.fields):
            if field.name == name:
                self.fields.pop(i)
                break

    def remove_fields(self, names: set[str]):
        if len(names) == 0:
            return
        filtered = []
        for field in self.fields:
            if field.name not in names:
                filtered.append(field)
        self.fields = filtered

    # 解析数组类型字段
    def parse_composite_fields(self):
        start = 0
        while start + 1 < len(self.fields):
            start = self.parse_one_array(start)

        names = set()
        for array in self.array_fields:
            for field in array.element_fields:
                names.add(field.name)
        self.remove_fields(names)

        start = 0
        while start < len(self.fields):
            start = self.parse_one_embed(start)

        names = set()
        for array in self.embed_fields:
            for name in array.field_names:
                names.add(name)
        self.remove_fields(names)

    # 能解析连续的2个数组定义，能跳过embed类型
    def parse_one_array(self, start: int) -> int:
        fields = []
        last_elem_prefix = ''
        last_array_idx = -1
        while start < len(self.fields):
            field = self.fields[start]
            prefix, idx = helper.parse_array_name_index(field.name)
            if prefix != '':
                if last_elem_prefix == '':
                    last_elem_prefix = prefix
                if prefix == last_elem_prefix and idx == last_array_idx + 1:
                    start += 1
                    fields.append(field)
                    last_array_idx = idx
                else:
                    start += 1
                    break
            else:
                if last_elem_prefix == '':
                    start += 1
                else:
                    break

        if len(fields) < 2:
            return start

        array = ArrayField()
        array.name = last_elem_prefix
        array.camel_case_name = helper.camel_case(last_elem_prefix)
        array.type_name = fields[0].type_name + '[]'
        for field in fields:
            array.element_fields.append(field)
        self.array_fields.append(array)

        return start

    # 解析嵌入类型的字段
    def parse_one_embed(self, start: int) -> int:
        all_range = []
        gap_fields = []
        while start < len(self.fields):
            field = self.fields[start]
            if field.name.endswith('[0]'):
                start += 1
                all_range.append(field.name)
                gap_fields.append(copy.deepcopy(field))
            else:
                if len(gap_fields) == 0:
                    start += 1
                else:
                    break

        if len(gap_fields) < 2:
            return start

        gap_len = len(gap_fields)
        index = 0
        while start + gap_len <= len(self.fields):
            index += 1
            match_count = 0
            for i in range(gap_len):
                field = self.fields[start + i]
                gap_field = gap_fields[i]
                expect_name = f'{gap_field.name[:-3]}[{index}]'
                if field.name == expect_name and field.type_name == gap_field.type_name:
                    match_count += 1
                else:
                    break

            if match_count != gap_len:
                break

            for i in range(gap_len):
                field = self.fields[start + i]
                all_range.append(field.name)
            start += gap_len

        if len(all_range) > 0:
            embed = EmbedField()
            for field in gap_fields:
                field.name = field.name[:-3]
                field.camel_case_name = field.camel_case_name[:-3]
                embed.element_fields.append(field)
            embed.field_names = all_range
            embed.generate_field_name()
            self.embed_fields.append(embed)
        return start
