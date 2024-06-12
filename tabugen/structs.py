# Copyright (C) 2024 ki7chen@github. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

from tabugen.util import helper


# 结构的字段
class StructField:

    def __init__(self):
        self.name = ''  # 字段名
        self.camel_case_name = ''  # 驼峰命名
        self.original_type_name = ''  # 原始类型名，可能是type alias
        self.type_name = ''  # 类型名
        self.type = 0  # 类型
        self.comment = ''  # 注释


class ArrayField:

    def __init__(self):
        self.name = ''
        self.camel_case_name = ''
        self.comment = ''
        self.type_name = ''
        self.original_field_names = set()


# 内嵌类型字段
class EmbedField:

    def __init__(self):
        self.name = ''
        self.camel_case_name = ''
        self.comment = ''
        self.class_name = ''
        self.field_name = ''
        self.gap_field_names = []
        self.original_field_names = set()

    def generate_field_name(self):
        result_name = ''
        for name in self.gap_field_names:
            name = helper.camel_to_snake(name)
            components = name.split('_')
            result_name += components[0].title()
        self.field_name = result_name
        self.class_name = 'T' + result_name


# 一个结构定义
class LangStruct:

    def __init__(self):
        self.name = ''
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
        return max_len

    # 获取字段类型最大长度
    def max_field_type_length(self, mapper=None):
        max_len = 0
        for field in self.fields:
            n = len(field.original_type_name)
            if mapper is not None:
                n = len(mapper(field.original_type_name))
            if n > max_len:
                max_len = n
        return max_len

    def remove_field_by_name(self, name: str):
        for i, field in enumerate(self.fields):
            if field.name == name:
                self.fields.pop(i)
                break

    def remove_fields(self, names: set[str]):
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

        for array in self.array_fields:
            self.remove_fields(array.original_field_names)

        start = 0
        while start < len(self.fields):
            start = self.parse_one_embed(start)

        for array in self.embed_fields:
            self.remove_fields(array.original_field_names)

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
            array.original_field_names.add(field.name)
        self.array_fields.append(array)

        return start

    # 解析嵌入类型的字段
    def parse_one_embed(self, start: int) -> int:
        all_range = []
        gap_names = []
        while start < len(self.fields):
            field = self.fields[start]
            if field.name.endswith('[0]'):
                start += 1
                all_range.append(field.name)
                gap_names.append(field.name[:-3])
            else:
                if len(gap_names) == 0:
                    start += 1
                else:
                    break

        if len(gap_names) < 2:
            return start

        gap_len = len(gap_names)
        index = 0
        while start + gap_len <= len(self.fields):
            index += 1
            match_count = 0
            for i in range(gap_len):
                field = self.fields[start + i]
                if field.name == f'{gap_names[i]}[{index}]':
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
            embed.gap_field_names = gap_names
            embed.original_field_names = set(all_range)
            embed.generate_field_name()
            self.embed_fields.append(embed)
        return start








