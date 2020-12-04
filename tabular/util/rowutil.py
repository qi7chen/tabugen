# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import sys
import csv
import codecs
import tabular.predef as predef
import tabular.util.strutil as strutil


def is_all_row_field_value_unique(rows, index):
    all_set = {}
    for i, row in rows:
        if len(row[index]) > 0:
            value = row[index]
            if value in all_set:
                return False, i, all_set[value]
            else:
                all_set[value] = i
    return True, 0, 0


# 检查唯一主键
def validate_unique_column(struct, rows):
    if struct['options'][predef.PredefParseKVMode]:
        return rows

    if predef.OptionUniqueColumns not in struct['options']:
        return rows
    names = struct['options'][predef.OptionUniqueColumns]
    if len(names) == 0:
        return rows
    for _, field in struct['fields']:
        if field['name'] in names:
            idx = field['column_index'] - 1
            (is_unique, row_line, exist_line) = is_all_row_field_value_unique(rows, idx)
            if not is_unique:
                print('duplicate field %s value found, row %d and row %d' % (field['name'], exist_line, row_line))
                sys.exit(1)
    return rows


# 置空不必要显示的内容
def hide_skipped_row_fields(enable_column_skip, struct, rows):
    if predef.PredefValueTypeColumn in struct['options']:
        typecol = int(struct['options'][predef.PredefValueTypeColumn])
        commentcol = int(struct['options'][predef.PredefCommentColumn])
        for row in rows:
            row[typecol - 1] = ''
            row[commentcol - 1] = ''
    else:
        if enable_column_skip:
            for row in rows:
                for field in struct["fields"]:
                    if not field["enable"]:
                        idx = field["column_index"] - 1
                        row[idx] = ''
    return rows