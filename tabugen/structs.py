# Copyright (C) 2024 qi7chen@github. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import json
import copy
import inflect
from dataclasses import dataclass, field
import tabugen.predef as predef
from tabugen.util import helper
from tabugen.util import tableutil
from tabugen.typedef import Type

plural_engine = inflect.engine()

# 结构的字段
@dataclass
class StructField:
    origin_name: str = ''       # 原始字段名
    name: str = ''              # 字段名
    camel_case_name: str = ''   # 驼峰命名
    origin_type_name: str = ''  # 原始类型名，可能是type alias
    type_name: str = ''         # 类型名
    type: Type = Type.Unknown   # 类型数值
    lang_type_name: str = ''    # 对应语言的类型名
    column: int = 0             # 所处列
    comment: str = ''           # 注释
    name_defval: str = ''


@dataclass
class ArrayField:
    name: str = ''              # 数组前缀名称
    field_name: str = ''        # 在结构中的字段名
    camel_case_name: str = ''
    comment: str = ''
    type_name: str = ''
    lang_type_name: str = ''
    element_fields: list[StructField] = field(default_factory=list)



# 一个结构定义
@dataclass
class Struct:
    filepath: str = ''
    name: str = ''
    camel_case_name: str = ''
    comment: str = ''
    parse_time: int = 0
    options: dict[str, str] = field(default_factory=dict)
    data_rows: list[list[str]] = field(default_factory=list)         # 数据
    field_names: list[str] = field(default_factory=list)
    field_columns: list[int] = field(default_factory=list)
    raw_fields: list[StructField] = field(default_factory=list)
    fields: list[StructField] = field(default_factory=list)
    array_fields: list[ArrayField] = field(default_factory=list)      # 数组字段
    kv_fields: list[StructField] = field(default_factory=list)        # kv字段

    def get_field_by_name(self, name: str) -> StructField | None:
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def get_column_index(self, name: str) -> int:
        for i, field in enumerate(self.fields):
            if field.name == name:
                return field.column
        return -1

    # 获取字段名最大长度
    def max_field_lang_var_length(self, camel_case=True) -> int:
        max_len = 0
        for field in self.fields:
            n = len(field.name_defval)
            if n > max_len:
                max_len = n
        for array in self.array_fields:
            if camel_case:
                n = len(array.camel_case_name)
            else:
                n = len(array.field_name)
            if n > max_len:
                max_len = n
        return max_len

    # 获取字段类型最大长度
    def max_field_lang_type_length(self):
        max_len = 0
        for field in self.fields:
            n = len(field.lang_type_name)
            if n > max_len:
                max_len = n
        for array in self.array_fields:
            n = len(array.lang_type_name)
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

    def has_array_field(self, name: str) -> bool:
        for array in self.array_fields:
            if array.name == name:
                return True
        return False

    # 解析数组类型字段
    def parse_array_fields(self):
        start = 0
        while start + 1 < len(self.fields):
            end = self.parse_one_array(start)
            if end - start > 0:
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
        fields = []
        elem_prefix = ''
        end = start
        for i in range(start, len(self.fields)):
            field = self.fields[i]
            if field.name.endswith('[0]'):
                elem_prefix = field.name[:-3]
                if not self.has_array_field(elem_prefix):
                    fields.append(copy.deepcopy(field))
                    end = i
                    break

        if end == start:
            return end

        start = end + 1
        max_round = len(self.fields) - start
        for n in range(1, max_round):
            target_name = elem_prefix + f'[{n}]'
            for i in range(start, len(self.fields)):
                field = self.fields[i]
                if field.name == target_name:
                    fields.append(copy.deepcopy(field))
                    start = i
                    break

        array = ArrayField()
        array.name = elem_prefix
        array.field_name = plural_engine.plural(elem_prefix)  # 单数转复数
        array.camel_case_name = helper.camel_case(elem_prefix)
        array.type_name = fields[0].type_name + '[]'
        array.comment = fields[0].comment
        for field in fields:
            array.element_fields.append(field)
        self.array_fields.append(array)

        return end

    def get_kv_key_col(self):
        return self.get_column_index(predef.PredefKVKeyName)

    def get_kv_type_col(self):
        return self.get_column_index(predef.PredefKVTypeName)

    def get_kv_value_col(self):
        return self.get_column_index(predef.PredefKVValueName)

    def get_kv_comment_col(self):
        for field in self.raw_fields:
            if field.name.startswith('#Desc'):
                return field.column
        return -1

    def get_kv_max_len(self, type_mapper=None, legacy=True) -> (int, int):
        max_name_len = 0
        max_type_len = 0
        key_idx = self.get_kv_key_col()
        type_idx = self.get_kv_type_col()
        for row in self.data_rows:
            key_name = row[key_idx]
            if len(key_name) > max_name_len:
                max_name_len = len(key_name)
            type_name = 'int'
            if type_idx >= 0:
                type_name = row[type_idx]
            if legacy and type_name.isdigit():
                type_name = tableutil.legacy_kv_type(int(type_name))
            n = len(type_name)
            if type_mapper is not None:
                n = len(type_mapper(type_name))
            if n > max_type_len:
                max_type_len = n
        return max_name_len, max_type_len
