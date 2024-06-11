# Copyright (C) 2018-present ki7chen@github. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

# 结构的字段
class StructField:

    def __init__(self):
        self.name = ''  # 字段名
        self.camel_case_name = ''  # 驼峰命名
        self.original_type_name = ''  # 原始类型名
        self.type_name = ''  # 类型名
        self.type = 0  # 类型
        self.comment = ''  # 注释


# 内嵌类型字段
class EmbedField:

    def __init__(self):
        self.name = ''
        self.camel_case_name = ''
        self.comment = ''
        self.n_fields = 0
        self.field_tuples = []


# 一个结构定义
class LangStruct:

    def __init__(self):
        self.name = ''
        self.fields = []
        self.options = {}
        self.camel_case_name = ''
        self.comment = ''
        self.file = ''
        self.parse_time = 0
        self.array_fields = {}  # 内嵌的数组字段
        self.embed_fields = []  # 内嵌类型字段
        self.data_rows = []  # 数据

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
