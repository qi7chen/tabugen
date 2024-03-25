# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import tabugen.predef as predef
import tabugen.typedef as types
import tabugen.util.strutil as strutil
import tabugen.util.tableutil as tableutil
import tabugen.parser.helper as helper


# 使用excel解析结构描述
class SpreadSheetFileParser:

    def __init__(self):
        self.file_dir = ''
        self.skip_names = ''
        self.with_data = True
        self.filenames = []
        self.project_kind = ''

    @staticmethod
    def name():
        return "excel"

    def init(self, args):
        self.file_dir = args.asset_path
        self.project_kind = args.project_kind
        if args.without_data:
            self.with_data = False
        if args.skip_files is not None:
            self.skip_names = [x.strip() for x in args.skip_files.split(' ')]
        self.enum_filenames(self.file_dir)

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
            filenames = helper.enum_spreadsheet_files(file_dir)
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

    def is_match_project_kind(self, col: str) -> bool:
        if self.project_kind == '':
            return True
        idx = col.find('_')
        if idx < 0:
            return True
        return col[:idx] == self.project_kind[0].title()

    @staticmethod
    def get_type_name(has_type_row, name: str, table, col: int):
        if has_type_row:
            type_row = table[predef.PredefFieldTypeDefRow]
            type_name = type_row[col]
        else:
            type_name = tableutil.field_type_from_name(name)

        if type_name == '':
            type_name = tableutil.infer_field_type(table, predef.PredefFieldTypeDefRow, col)
        if types.is_valid_type_name(type_name):
            return type_name
        else:
            return 'string'

    def parse_struct_table(self, has_type_row, meta, table, struct):
        class_name = meta[predef.PredefClassName]
        assert len(class_name) > 0
        struct['name'] = class_name
        struct['camel_case_name'] = strutil.camel_case(class_name)

        name_row = table[predef.PredefFieldNameRow]

        fields_names = {}
        prev_field = None
        for col, name in enumerate(name_row):
            # skip empty column
            if name == '' or name.startswith('#') or name.startswith('//') :
                continue
            if not self.is_match_project_kind(name):
                continue

            type_name = self.get_type_name(has_type_row, name, table, col)
            assert type_name != ''
            field_type = types.get_type_by_name(type_name)

            assert name not in fields_names, name
            fields_names[name] = True

            field = {
                "name": name,
                "camel_case_name": strutil.camel_case(name),
                "original_type_name": type_name,
                "type_name": types.get_name_of_type(field_type),
                "type": field_type,
                "comment": '',
            }

            if prev_field is not None:
                is_vector = strutil.is_vector_fields(prev_field, field)
                # print('is vector', is_vector, prev_field, field)
                if is_vector:
                    prev_field["is_vector"] = True
                    field["is_vector"] = True
            prev_field = field

            assert field["type"] != types.Type.Unknown
            assert field["type_name"] != ""

            struct['fields'].append(field)

    # 解析数据列
    def parse_data_sheet(self, meta, table):
        struct = {
            'fields': [],
            'options': meta,
            'comment': meta.get(predef.PredefClassComment, ""),
        }
        data_start_row = 1
        has_type_row = False
        if len(table) >= 2:
            if tableutil.is_type_row(table[predef.PredefFieldTypeDefRow]):
                has_type_row = True
                data_start_row += 1
        self.parse_struct_table(has_type_row, meta, table, struct)
        if self.with_data:
            data = table[data_start_row:]
            data = strutil.pad_data_rows(table[data_start_row], data)
            struct["data_rows"] = data
        return struct

    # 解析所有文件
    def parse_all(self):
        descriptors = []
        for filename in self.filenames:
            print(strutil.current_time(), "start parse", filename)
            struct = self.parse_one_file(filename)
            if struct is None:
                print('parse file %s failed' % filename)
            else:
                struct['source'] = filename
                descriptors.append(struct)
        return descriptors

    # 解析单个文件
    def parse_one_file(self, filename):
        table, meta = helper.read_workbook_table(filename)
        table = tableutil.table_remove_empty(table)
        struct = self.parse_data_sheet(meta, table)
        struct['name'] = meta[predef.PredefClassName]
        struct['camel_case_name'] = strutil.camel_case(struct['name'])
        struct['file'] = os.path.basename(filename)
        if predef.PredefInnerTypeClass in meta:
            struct['inner_fields'] = tableutil.parse_inner_fields(struct)
        return struct
