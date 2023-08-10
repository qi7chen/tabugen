"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import os
import tabugen.predef as predef
import tabugen.typedef as types
import tabugen.util.strutil as strutil
import tabugen.util.tableutil as tableutil
import tabugen.parser.xlsxhelp as xlsxhelp


# 使用excel解析结构描述
class ExcelStructParser:

    def __init__(self):
        self.filedir = ''
        self.skip_names = ''
        self.with_data = True
        self.filenames = []
        self.project_kind = ''

    @staticmethod
    def name():
        return "excel"

    def init(self, args):
        self.filedir = args.asset_path
        self.project_kind = args.project_kind
        if args.without_data:
            self.with_data = False
        if args.skip_files is not None:
            self.skip_names = [x.strip() for x in args.skip_files.split(' ')]
        self.enum_filenames(self.filedir)

    # 跳过忽略的文件名
    def enum_filenames(self, filedir: str):
        filenames = []
        if not os.path.exists(filedir):
            print('file path [%s] not exist' % filedir)
            return

        # filename is a directory
        if os.path.isdir(filedir):
            filedir = os.path.abspath(filedir)
            print('parse files in directory:', filedir)
            filenames = xlsxhelp.enum_excel_files(filedir)
        else:
            assert os.path.isfile(filedir)
            filename = os.path.abspath(filedir)
            filenames.append(filename)

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

    def parse_kv_table(self, table, struct):
        key_col = tableutil.find_col_by_name(table[predef.PredefFieldNameRow], predef.PredefKVKeyName)
        type_col = tableutil.find_col_by_name(table[predef.PredefFieldNameRow], predef.PredefKVTypeName)
        val_col = tableutil.find_col_by_name(table[predef.PredefFieldNameRow], predef.PredefKVValueName)
        comment_col = tableutil.find_col_by_name(table[predef.PredefFieldNameRow], predef.PredefKVCommentName)
        struct['options']['key_column'] = key_col
        struct['options']['type_column'] = type_col
        struct['options']['value_column'] = val_col
        struct['options']['comment_column'] = comment_col
        data_rows = table[predef.PredefDataStartRow:]
        for row in data_rows:
            name = row[key_col]
            type_name = row[type_col]
            field_type = types.get_type_by_name(type_name)
            comment = ''
            if comment_col >= 0:
                comment = row[comment_col]
            field = {
                "name": name,
                "camel_case_name": strutil.camel_case(name),
                "original_type_name": type_name,
                "type": field_type,
                "type_name": types.get_name_of_type(field_type),
                "comment": comment,
            }
            struct['fields'].append(field)

    def is_match_project_kind(self, col: str) -> bool:
        if self.project_kind == '':
            return True
        idx = col.find('_')
        if idx < 0:
            return True
        return col[:idx] == self.project_kind[0].title()

    def parse_struct_table(self, meta, table, struct):
        if len(table) <= predef.PredefDataStartRow:
            return

        class_name = meta[predef.PredefClassName]
        assert len(class_name) > 0
        struct['name'] = class_name
        struct['camel_case_name'] = strutil.camel_case(class_name)

        type_row = table[predef.PredefFieldTypeRow]
        comment_row = table[predef.PredefCommentRow]
        name_row = table[predef.PredefFieldNameRow]

        fields_names = {}
        prev_field = None
        for col, name in enumerate(name_row):
            # skip empty column
            if name == '' or name.startswith('#') or name.startswith('//') or type_row[col] == "":
                continue
            if not self.is_match_project_kind(name):
                continue

            name = tableutil.parse_head_field(name)
            field_type = types.get_type_by_name(type_row[col])

            assert name not in fields_names, name
            fields_names[name] = True

            field = {
                "name": name,
                "camel_case_name": strutil.camel_case(name),
                "original_type_name": type_row[col],
                "type": field_type,
                "type_name": types.get_name_of_type(field_type),
                "comment": comment_row[col],
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
        if meta[predef.PredefParseKVMode]:  # 全局KV模式
            self.parse_kv_table(table, struct)
        else:
            self.parse_struct_table(meta, table, struct)

        if self.with_data:
            data = table[predef.PredefDataStartRow:]
            data = strutil.pad_data_rows(struct['fields'], data)
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
        data_table, meta = xlsxhelp.read_workbook_data(filename)
        if predef.PredefParseKVMode in meta:
            text = meta[predef.PredefParseKVMode]
            meta[predef.PredefParseKVMode] = strutil.str2bool(text)
        else:
            meta[predef.PredefParseKVMode] = False

        struct = self.parse_data_sheet(meta, data_table)
        struct['name'] = meta[predef.PredefClassName]
        struct['camel_case_name'] = strutil.camel_case(struct['name'])
        struct['file'] = os.path.basename(filename)
        if predef.PredefInnerTypeClass in meta:
            struct['inner_fields'] = tableutil.parse_inner_fields(struct)
        return struct
