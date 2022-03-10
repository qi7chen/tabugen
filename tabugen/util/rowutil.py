# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import sys
import typing

import tabugen.predef as predef


# 是否字段内容唯一
def is_all_row_field_value_unique(rows: typing.Sequence, index: int) -> typing.Tuple:
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
def validate_unique_column(struct: typing.Mapping, rows: typing.Sequence):
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


# 只保留enable的field
def shrink_enabled_rows(rows: typing.Sequence, struct: typing.Mapping):
    new_rows = []
    for row in rows:
        new_row = []
        for field in struct['fields']:
            if field['enable']:
                idx = field['column_index'] - 1
                new_row.append(row[idx])
        new_rows.append(new_row)
    return new_rows


# 置空不必要显示的内容
def hide_skipped_row_fields(struct: typing.Mapping, rows: typing.Sequence):
    if predef.PredefValueTypeColumn in struct['options']:
        # 把KV模式的类型和注释从csv中删除
        typecol = int(struct['options'][predef.PredefValueTypeColumn])
        commentcol = int(struct['options'][predef.PredefCommentColumn])
        for row in rows:
            row[typecol - 1] = ''
            row[commentcol - 1] = ''
    return rows
