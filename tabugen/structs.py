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
        self.column = 0


class ArrayField:

    def __init__(self):
        self.field_name = ''
        self.camel_case_name = ''
        self.comment = ''
        self.type_name = ''
        self.element_fields: list[StructField] = []


# 一个结构定义
class Struct:

    def __init__(self):
        self.name = ''
        self.camel_case_name = ''
        self.comment = ''
        self.parse_time = 0
        self.options = {}
        self.data_rows = []  # 数据
        self.raw_fields: list[StructField] = []
        self.fields: list[StructField] = []
        self.array_fields: list[ArrayField] = []  # 数组字段

    def get_field_by_name(self, name: str) -> StructField | None:
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def get_column_index(self, name: str) -> int:
        for i, field in enumerate(self.fields):
            if field.name == name:
                return i
        return -1

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
    def parse_array_fields(self):
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
        array.field_name = last_elem_prefix + 'List'
        array.camel_case_name = helper.camel_case(last_elem_prefix)
        array.type_name = fields[0].type_name + '[]'
        for field in fields:
            array.element_fields.append(field)
        self.array_fields.append(array)

        return end

