
class StructField:

    def __init__(self):
        self.name = ''
        self.camel_case_name = ''
        self.original_type_name = ''
        self.type_name = ''
        self.type = 0
        self.comment = ''


class EmbedField:

    def __init__(self):
        self.name = ''
        self.camel_case_name = ''
        self.comment = ''
        self.n_fields = 0
        self.field_tuples = []


class LangStruct:

    def __init__(self):
        self.name = ''
        self.fields = []
        self.options = {}
        self.camel_case_name = ''
        self.comment = ''
        self.file = ''
        self.parse_time = 0
        self.array_fields = {}      # 内嵌的数组字段
        self.embed_fields = []      # 内嵌类型字段
        self.data_rows = []         # 数据

    def max_field_name_length(self):
        max_len = 0
        for field in self.fields:
            n = len(field.name)
            if n > max_len:
                max_len = n
        return max_len

    def max_field_type_length(self, mapper=None):
        max_len = 0
        for field in self.fields:
            n = len(field.original_type_name)
            if mapper is not None:
                n = len(mapper(field.original_type_name))
            if n > max_len:
                max_len = n
        return max_len
