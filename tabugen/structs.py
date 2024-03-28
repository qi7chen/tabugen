
class StructField:

    def __init__(self):
        self.name = ''
        self.camel_case_name = ''
        self.original_type_name = ''
        self.type_name = ''
        self.type = 0
        self.comment = ''


class LangStruct:

    def __init__(self):
        self.name = ''
        self.fields = []
        self.options = {}
        self.camel_case_name = ''
        self.comment = ''
        self.file = ''
        self.parse_time = 0
        self.array_field_names = {}
        self.composite_type_names = []

