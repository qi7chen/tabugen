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
        self.field_name = ''
        self.camel_case_name = ''
        self.comment = ''
        self.type_name = ''
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
        for array in self.array_fields:
            n = len(array.field_name)
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
        for array in self.array_fields:
            n = len(array.type_name)
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
            end = self.parse_one_array(start)
            if end - start > 1:
                start = end
            else:
                break

        names = set()
        for array in self.array_fields:
            for field in array.element_fields:
                names.add(field.name)
        self.remove_fields(names)

        start = 0
        while start < len(self.fields):
            end = self.parse_one_embed(start)
            if end - start > 1:
                start = end
            else:
                break

        names = set()
        for array in self.embed_fields:
            for name in array.field_names:
                names.add(name)
        self.remove_fields(names)

    # 解析数组定义
    def parse_one_array(self, start: int) -> int:
        last_elem_prefix = ''
        last_array_idx = -1
        end = start
        for i in range(start, len(self.fields)):
            field = self.fields[i]
            prefix, idx = helper.parse_array_name_index(field.name)
            if prefix != '':
                if last_elem_prefix == '':
                    last_elem_prefix = prefix
                    start = i
                    end = start
                if prefix == last_elem_prefix and idx == last_array_idx + 1:
                    end += 1
                    last_array_idx = idx
                else:
                    break
            else:
                # new array field
                if last_elem_prefix != '':
                    break

        if end - start < 2:
            return end

        fields = []
        for i in range(start, end):
            field = self.fields[i]
            fields.append(copy.deepcopy(field))

        array = ArrayField()
        array.field_name = last_elem_prefix
        array.camel_case_name = helper.camel_case(last_elem_prefix)
        array.type_name = fields[0].type_name + '[]'
        for field in fields:
            array.element_fields.append(field)
        self.array_fields.append(array)

        return end

    # 解析嵌入类型的字段
    def parse_one_embed(self, start: int) -> int:
        all_range = []
        gap_fields = []
        end = start
        last_elem_prefix = ''
        for i in range(start, len(self.fields)):
            field = self.fields[i]
            prefix, idx = helper.parse_array_name_index(field.name)
            if prefix != '' and idx == 0:
                if last_elem_prefix == '':
                    start = i
                    end = start
                if prefix != last_elem_prefix:
                    end += 1
                    last_elem_prefix = prefix
                    all_range.append(field.name)
                    gap_fields.append(copy.deepcopy(field))
                else:
                    break
            else:
                if len(gap_fields) > 0:
                    break

        if end - start < 2:
            return end

        gap_len = len(gap_fields)
        index = 0
        for i in range(end, len(self.fields), gap_len):
            match_count = 0
            index += 1
            for j in range(gap_len):
                field = self.fields[i + j]
                gap_field = gap_fields[j]
                expect_name = f'{gap_field.name[:-3]}[{index}]'
                if field.name == expect_name and field.type_name == gap_field.type_name:
                    match_count += 1
                else:
                    break

            if match_count != gap_len:
                break

            for j in range(gap_len):
                field = self.fields[i + j]
                all_range.append(field.name)
            end += gap_len

        if len(all_range) > 0:
            embed = EmbedField()
            for field in gap_fields:
                field.name = field.name[:-3]
                field.camel_case_name = field.camel_case_name[:-3]
                embed.element_fields.append(field)
            embed.field_names = all_range
            embed.generate_field_name()
            self.embed_fields.append(embed)
        return end
