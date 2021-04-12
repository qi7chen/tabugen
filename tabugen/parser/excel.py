# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import sys
import tabugen.predef as predef
import tabugen.typedef as types
import tabugen.util.strutil as strutil
import tabugen.util.structutil as structutil
import tabugen.util.fieldutil as fieldutil
import tabugen.parser.xlsxhelp as xlsxhelp


# 使用excel解析结构描述
class ExcelStructParser:

    def __init__(self):
        self.filedir = ''
        self.skip_names = ''
        self.metafile = ''
        self.with_data = True
        self.filenames = []
        self.meta_index = {}
        self.enable_field_skipping = False

    @staticmethod
    def name():
        return "excel"

    def init(self, args):
        self.filedir = args.parse_files
        if args.without_data:
            self.with_data = False
        if args.enable_column_skip:
            self.enable_field_skipping = True
        if args.parse_file_skip is not None:
            self.skip_names = args.parse_file_skip.split(' ')
        self.metafile = args.parse_meta_file
        self.make_filenames(self.filedir)

    # 跳过忽略的文件名
    def make_filenames(self, filedir):
        filenames = []
        if not os.path.exists(filedir):
            print('file path [%s] not exist' % filedir)
            sys.exit(1)
        if os.path.isdir(filedir):  # filename is a directory
            filedir = os.path.abspath(filedir)
            print('parse files in directory:', filedir)
            filenames = strutil.enum_files(filedir, xlsxhelp.is_ignored_filename)
        else:
            assert os.path.isfile(filedir)
            filename = os.path.abspath(filedir)
            filenames.append(filename)

        if len(self.skip_names) > 0:
            print('skipped file names:', self.skip_names)
        for filename in filenames:
            ignored = False
            for skip_name in self.skip_names:
                skip_name = skip_name.strip()
                if len(skip_name) > 0:
                    if filename.find(skip_name) >= 0:
                        ignored = True
            if not ignored:
                self.filenames.append(filename)

    def parse_meta_file(self):
        assert os.path.isfile(self.metafile)
        wb, sheet_names = xlsxhelp.read_workbook_and_sheet_names(self.metafile)
        if predef.PredefMetaSheet not in sheet_names:
            raise RuntimeError('sheet %s not found in file %s' % (predef.PredefMetaSheet, self.metafile))
        sheet_rows = xlsxhelp.read_workbook_sheet_to_rows(wb, predef.PredefMetaSheet)
        xlsxhelp.close_workbook(wb)

        last_row = 0
        for i in range(len(sheet_rows)):
            row = sheet_rows[i]
            if i > last_row and strutil.is_row_empty(row):
                rows = sheet_rows[last_row:i]
                last_row = i + 1
                meta = fieldutil.parse_meta_rows(rows)
                assert predef.PredefTargetFileName in meta
                target_filename = meta[predef.PredefTargetFileName]
                pair = target_filename.split('@')
                if len(pair) == 2:
                    target_filename = pair[0].strip()
                    sheet_name = pair[1].strip()
                    if len(sheet_name) > 0:
                        meta[predef.PredefTargetFileSheet] = sheet_name
                assert os.path.isfile(target_filename)
                assert target_filename not in self.meta_index
                self.meta_index[target_filename] = meta

    # 获取一个sheet的meta信息
    def get_file_meta(self, filename, wb, sheet_names):
        # 优先本文件
        if predef.PredefMetaSheet in sheet_names:
            sheet_rows = xlsxhelp.read_workbook_sheet_to_rows(wb, predef.PredefMetaSheet)
            meta = fieldutil.parse_meta_rows(sheet_rows)
            return fieldutil.validated_meta(meta)
        else:
            meta = self.meta_index.get(filename)
            if meta is None:
                meta = {predef.PredefClassName: sheet_names[0]}
            return fieldutil.validated_meta(meta)

    # 解析数据列
    def parse_data_sheet(self, meta, rows):
        assert len(rows) > 0

        # validate meta index
        type_index = int(meta[predef.PredefStructTypeRow])
        assert type_index < len(rows), type_index
        name_index = int(meta[predef.PredefStructNameRow])
        assert name_index < len(rows), name_index
        data_start_index = int(meta[predef.PredefDataStartRow])
        data_end_index = len(rows)
        if predef.PredefDataEndRow in meta:
            data_end_index = int(meta[predef.PredefDataEndRow])
            assert data_end_index <= len(rows), data_end_index
        assert data_start_index < len(rows), data_start_index
        assert data_start_index <= data_end_index, data_end_index

        struct = {
            'fields': [],
            'comment': meta.get(predef.PredefClassComment, ""),
        }

        class_name = meta[predef.PredefClassName]
        assert len(class_name) > 0
        struct['name'] = class_name
        struct['camel_case_name'] = strutil.camel_case(class_name)

        comment_index = -1
        if predef.PredefCommentRow in meta:
            index = int(meta[predef.PredefCommentRow])
            if index > 0:
                comment_index = index - 1  # to zero-based

        type_row = rows[type_index - 1]
        name_row = rows[name_index - 1]
        fields_names = {}
        prev_field = None
        for i in range(len(type_row)):
            if meta[predef.PredefParseKVMode]:  # 全局KV模式
                continue
            if type_row[i] == "" or name_row[i] == "":  # skip empty column
                continue
            ftype = types.get_type_by_name(type_row[i])
            field = {
                "name": name_row[i],
                "camel_case_name": strutil.camel_case(name_row[i]),
                "original_type_name": type_row[i],
                "type": ftype,
                "type_name": types.get_name_of_type(ftype),
                "column_index": i + 1,
            }

            assert field["name"] not in fields_names, field["name"]
            fields_names[field["name"]] = True

            if prev_field is not None:
                is_vector = strutil.is_vector_fields(prev_field, field)
                # print('is vector', is_vector, prev_field, field)
                if is_vector:
                    prev_field["is_vector"] = True
                    field["is_vector"] = True
            prev_field = field

            assert field["type"] != types.Type_Unknown
            assert field["type_name"] != ""

            field["comment"] = " "
            if comment_index > 0:
                field["comment"] = rows[comment_index][i]

            field["enable"] = True
            if self.enable_field_skipping and predef.OptionSkippedColumns in meta and len(
                    meta[predef.OptionSkippedColumns]) > 0:
                if field["name"] in meta[predef.OptionSkippedColumns]:
                    field["enable"] = False

            # print(field)
            struct['fields'].append(field)

        struct["options"] = meta
        if self.with_data:
            data_rows = rows[data_start_index - 1: data_end_index]
            data_rows = strutil.pad_data_rows(data_rows, struct)
            data_rows = xlsxhelp.validate_data_rows(data_rows, struct)
            struct["data_rows"] = data_rows
        return struct

    # 解析所有文件
    def parse_all(self):
        descriptors = []
        if self.metafile is not None:
            self.parse_meta_file()

        for filename in self.filenames:
            print(strutil.current_time(), "start parse", filename)
            struct = self.parse_one_file(filename)
            if struct is None:
                print('parse file %s failed' % filename)
            else:
                structutil.setup_struct(struct)
                struct['source'] = filename
                descriptors.append(struct)
        return descriptors

    # 解析单个文件
    def parse_one_file(self, filename):
        wb, sheet_names = xlsxhelp.read_workbook_and_sheet_names(filename)
        if len(sheet_names) == 0:
            print('%s has no sheet' % filename)
            return

        meta = self.get_file_meta(filename, wb, sheet_names)
        fieldutil.setup_meta_kv_mode(meta)
        xlsxhelp.close_workbook(wb)
        if meta is None:
            raise RuntimeError("not meta found for file %s" % filename)
        else:
            sheet_name = meta.get(predef.PredefTargetFileSheet, sheet_names[0])  # 没有指定就使用第一个sheet
            sheet_data = xlsxhelp.read_workbook_sheet_to_rows(wb, sheet_name)
            struct = self.parse_data_sheet(meta, sheet_data)
            struct['file'] = os.path.basename(filename)
            return struct


def unit_test(self):
    filename = u'''新建筑.xlsx'''
    parser = ExcelStructParser()
    parser.init('file=%s' % filename)
    all = parser.parser_all()
    print(strutil.current_time(), 'done')
    assert len(all) > 0
    for struct in all:
        print(struct)


if __name__ == '__main__':
    unit_test
