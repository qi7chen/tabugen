# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import unittest
import openpyxl
import descriptor
import predef
import util


class ExcelImporter:

    def __init__(self):
        self.options = []
        self.filenames = []
        self.meta = {}

    @staticmethod
    def name():
        return "excel"


    def initialize(self, argtext):
        self.options = util.parse_args(argtext)
        self.make_filenames()


    def enum_files(self, rootdir):
        files = []
        for dirpath, dirnames, filenames in os.walk(rootdir):
            for filename in filenames:
                 if filename.endswith(".xlsx"):
                     files.append(dirpath + os.sep + filename)
        filenames = []
        for filename in files:
            if not util.is_ignored_filename(filename):
                filenames.append(filename)
        return filenames


    def make_filenames(self):
        filenames = []
        filedir = self.options.get(predef.PredefFileDirOption, "")
        if filedir != "":
            print('parse files in directory:', filedir)
            filenames = self.enum_files(filedir)

        filename = self.options.get(predef.PredefFilenameOption, "")
        if filename != "":
            filenames.append(filename)

        skip_names = []
        if self.options.get(predef.PredefSkipFileOption, "") != "":
            skip_names = self.options[predef.PredefSkipFileOption].split(' ')

        for filename in filenames:
            ignored = False
            for skip_name in skip_names:
                skip_name = skip_name.strip()
                if len(skip_name) > 0:
                    if filename.find(skip_name) >= 0:
                        ignored = True
            if not ignored:
                self.filenames.append(filename)
        # print(self.filenames)


    def parse_meta_sheet(self, sheet):
        rows = util.read_sheet_to_csv(sheet)
        meta = {}
        for row in rows:
            if len(row) >= 2:
                key = row[0].strip()
                value = row[1].strip()
                if key != "" and value != "":
                    meta[key] = value

        # default values
        if predef.PredefStructTypeRow not in meta:
            meta[predef.PredefStructTypeRow] = "1"  # 类型列
        if predef.PredefStructNameRow not in meta:
            meta[predef.PredefStructNameRow] = "2"  # 名称列
        if predef.PredefCommentRow not in meta:
            meta[predef.PredefCommentRow] = "3"     # 注释列
        if predef.PredefDataStartRow not in meta:
            meta[predef.PredefDataStartRow] = "4"   # 数据起始列

        self.meta = meta


    def parse_data_sheet(self, sheet):
        rows = util.read_sheet_to_csv(sheet)
        assert len(rows) > 0

        # validate meta index
        type_index = int(self.meta[predef.PredefStructTypeRow])
        assert type_index < len(rows), type_index
        name_index = int(self.meta[predef.PredefStructNameRow])
        assert name_index < len(rows), name_index
        data_start_index = int(self.meta[predef.PredefDataStartRow])
        data_end_index = len(rows)
        if predef.PredefDataEndRow in self.meta:
            data_end_index = int(self.meta[predef.PredefDataEndRow])
            assert data_end_index <= len(rows), data_end_index
        assert data_start_index < len(rows), data_start_index
        assert data_start_index <= data_end_index, data_end_index

        struct = {}
        struct['fields'] = []

        struct['comment'] = self.meta.get(predef.PredefClassComment, "")

        class_name = sheet.title
        if predef.PredefClassName in self.meta:
            class_name = self.meta[predef.PredefClassName]
        assert len(class_name) > 0
        struct['name'] = class_name
        struct['camel_case_name'] = util.camel_case(class_name)

        comment_index = -1
        if predef.PredefCommentRow in self.meta:
            index = int(self.meta[predef.PredefCommentRow])
            if index > 0:
                comment_index = index - 1   # to zero-based

        type_row = rows[type_index - 1]
        name_row = rows[name_index - 1]
        fields_names = {}
        prev_field = None
        for i in range(len(type_row)):
            if type_row[i] == "" or name_row[i] == "":  # skip empty column
                continue
            field = {}
            field["name"] = name_row[i]
            field["camel_case_name"] = util.camel_case(name_row[i])
            field["original_type_name"] = type_row[i]
            field["type"] = descriptor.get_type_by_name(type_row[i])
            field["type_name"] = descriptor.get_name_of_type(field["type"])
            field["column_index"] = i + 1

            assert field["name"] not in fields_names, field["name"]
            fields_names[field["name"]] = True

            if prev_field is not None and util.is_vector_fields(prev_field, field):
                prev_field["is_vector"] = True
                field["is_vector"] = True
            prev_field = field

            assert field["type"] != descriptor.Type_Unknown
            assert field["type_name"] != ""

            field["comment"] = " "
            if comment_index > 0:
                field["comment"] = rows[comment_index][i]

            # print(field)
            struct['fields'].append(field)

        data_rows = rows[data_start_index - 1: data_end_index]
        data_rows = self.pad_data_rows(data_rows, struct)
        data_rows = self.validate_data_rows(data_rows, struct)
        struct["options"] = self.meta
        struct["data-rows"] = data_rows

        return struct


    def pad_data_rows(self, rows, struct):
        # pad empty row
        max_row_len = len(struct['fields'])
        for row in rows:
            if len(row) > max_row_len:
                max_row_len = len(row)

        for i in range(len(row)):
            for j in range(len(row), max_row_len):
                rows[i].append("")
        return rows


    # 将excel里配置为整数，但存储形式为浮点的进行四舍五入
    def validate_data_rows(self, rows, struct):
        new_rows = []
        fields = struct['fields']
        for row in rows:
            assert len(row) >= len(fields), (len(fields), len(row), row)
            for j in range(len(row)):
                if j >= len(fields):
                    continue
                typename = fields[j]['type_name']
                if descriptor.is_integer_type(typename) and len(row[j]) > 0:
                    f = float(row[j])  # test if ok
                    if row[j].find('.') >= 0:
                        print('round interger', row[j], '-->', round(f))
                        row[j] = str(round(float(row[j])))
                else:
                    if descriptor.is_floating_type(typename) and len(row[j]) > 0:
                        f = float(row[j])  # test if ok

            # skip all empty row
            is_all_empty = True
            for text in row:
                if len(text.strip()) > 0:
                    is_all_empty = False
                    break
            if not is_all_empty:
                new_rows.append(row)
        return new_rows


    # import all
    def import_all(self):
        descriptors = []
        for filename in self.filenames:
            print("start parse", filename)
            wb = openpyxl.load_workbook(filename, data_only=True)
            descriptor = self.import_one(wb)
            descriptors.append(descriptor)
        return descriptors


    def import_one(self, wb):
        sheet_names = wb.sheetnames
        assert len(sheet_names) > 0
        sheet = wb[predef.PredefMetaSheet]
        assert sheet is not None
        self.parse_meta_sheet(sheet)
        sheet = wb[sheet_names[0]]
        assert sheet is not None
        return self.parse_data_sheet(sheet)



class TestExcelImporter(unittest.TestCase):

    def test_enum_file(self):
        filename = '''E:\Projects\Client\Documents\新表\兵种.xlsx'''
        importer = ExcelImporter()
        importer.initialize('filename=%s' % filename)
        importer.import_all()


if __name__ == '__main__':
    unittest.main()