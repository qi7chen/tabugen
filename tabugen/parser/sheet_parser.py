# Copyright (C) 2018-present ki7chen@github. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import time
import tabugen.predef as predef
import tabugen.typedef as types
import tabugen.structs as structs
import tabugen.util.helper as helper
import tabugen.util.tableutil as tableutil
import tabugen.parser.toolkit as toolkit


# 使用excel解析结构描述
class SpreadSheetParser:

    def __init__(self):
        self.skip_names = ''    # 忽略解析的文件名
        self.with_data = True   # 是否包含数据
        self.filenames = []     # 文件名列表
        self.project_kind = ''  # 项目类型
        self.legacy = False     # 是否兼容旧模式

    @staticmethod
    def name():
        return "excel"

    # 初始化导出参数
    def init(self, args):
        self.legacy = args.legacy
        self.project_kind = args.project_kind
        if args.without_data:
            self.with_data = False
        if args.file_skip:
            self.skip_names = [x.strip() for x in args.file_skip]
        for filepath in args.file_asset:
            self.enum_filenames(filepath)

    # 跳过忽略的文件名
    def enum_filenames(self, file_dir: str):
        filenames = []
        if not os.path.exists(file_dir):
            print('file path [%s] not exist' % file_dir)
            return

        # filename is a directory
        if os.path.isdir(file_dir):
            file_dir = os.path.abspath(file_dir)
            print('parse files in directory:', file_dir)
            filenames = toolkit.enum_spreadsheet_files(file_dir)
        elif os.path.isfile(file_dir):
            filename = os.path.abspath(file_dir)
            filenames.append(filename)
        else:
            return

        if len(self.skip_names) == 0:
            self.filenames = filenames
            return

        print('skipped file names:', self.skip_names)
        for filename in filenames:
            ignored = False
            for skip_name in self.skip_names:
                if len(skip_name) > 0:
                    if filename.find(skip_name) >= 0:
                        ignored = True
                        break
            if not ignored:
                self.filenames.append(filename)

    # 用于指定导出字段时做筛选
    def is_match_project_kind(self, kind_name: str) -> bool:
        if self.project_kind == '' or kind_name == '':
            return True
        if kind_name == self.project_kind:
            return True
        if self.legacy and kind_name == 'A':  # A表示所有
            return True
        return False

    # 推到字段类型
    @staticmethod
    def deduce_type_name(has_type_row: bool, type_name: str,  col: int, table):
        # 有类型定义列
        if type_name == '' and has_type_row:
            type_name = table[predef.PredefFieldTypeDefRow][col]

        if type_name == '':  # 从内容列中推导出类型
            type_name = tableutil.infer_field_type(table, predef.PredefFieldTypeDefRow, col)

        if type_name in types.alias:
            type_name = types.alias[type_name]

        if type_name == 'map':
            type_name = tableutil.infer_field_map_type(table, predef.PredefFieldTypeDefRow, col)
        if type_name == 'array':
            type_name = tableutil.infer_field_array_type(table, predef.PredefFieldTypeDefRow, col)

        if types.is_valid_type_name(type_name):
            return type_name
        else:
            return 'string'

    def parse_struct(self, has_type_row, meta, table, struct: structs.Struct):
        class_name = meta[predef.PredefClassName]
        assert len(class_name) > 0
        struct.name = class_name
        struct.camel_case_name = helper.camel_case(class_name)

        name_row = table[predef.PredefFieldNameRow]

        duplicate_field_names = set()

        for col, name in enumerate(name_row):
            # 带换行的是注释
            comment = ''
            idx = name.find('\n')
            if idx > 0:
                comment = name[idx + 1:].replace('\n', ' ')
                name = name[:idx]

            field_type = types.Type.String
            field_name, type_name, kind_name = name, 'string', ''
            if not name.startswith('#'):
                kind_name, type_name, field_name = tableutil.split_field_name(name)
                if not self.is_match_project_kind(kind_name):
                    continue

                type_name = self.deduce_type_name(has_type_row, type_name, col, table)
                assert type_name != ''
                field_type = types.get_type_by_name(type_name)

            assert field_name not in duplicate_field_names, f'{field_name}'
            duplicate_field_names.add(field_name)

            field = structs.StructField()
            field.column = col
            field.origin_name = name
            field.name = field_name
            field.comment = comment
            field.camel_case_name = helper.camel_case(field_name)
            field.origin_type_name = type_name
            field.type_name = types.get_name_of_type(field_type)
            field.type = types.get_type_by_name(field.type_name)
            if not name.startswith('#'):
                struct.fields.append(field)
            struct.raw_fields.append(field)
            struct.field_names.append(field_name)
            struct.field_columns.append(col)

    # 解析数据列
    def parse_table_struct(self, meta: dict, table: list[list[str]]) -> structs.Struct:
        struct = structs.Struct()
        struct.comment = meta.get(predef.PredefClassComment, '')

        data_start_row = 1
        has_type_row = False
        if len(table) >= 2:
            if tableutil.is_type_row(table[predef.PredefFieldTypeDefRow]):
                has_type_row = True
                data_start_row += 1
        self.parse_struct(has_type_row, meta, table, struct)
        if self.with_data:
            data = table[data_start_row:]
            if len(data) > 0:
                data = helper.pad_data_rows(table[data_start_row], data)
            struct.data_rows = data
        return struct

    # 解析所有文件
    def parse_all(self):
        descriptors = []
        for filename in self.filenames:
            # print(helper.current_time(), "start parse", filename)
            struct = self.parse_one_file(filename)
            if struct is None:
                print('parse file %s failed' % filename)
            else:
                struct.file = filename
                descriptors.append(struct)
        return descriptors

    # 解析单个文件
    def parse_one_file(self, filename):
        start_at = time.time()
        base_filename = os.path.basename(filename)
        meta = {}
        table = toolkit.read_workbook_table(filename, meta)
        table = tableutil.trim_empty_columns(table)
        struct = self.parse_table_struct(meta, table)
        struct.filepath = base_filename
        struct.parse_array_fields()
        elapsed = time.time() - start_at
        struct.name = meta[predef.PredefClassName]
        struct.camel_case_name = helper.camel_case(struct.name)
        struct.parse_time = elapsed
        struct.options = meta
        return struct

