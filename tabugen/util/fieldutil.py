# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import typing
import tabugen.predef as predef


# KV模式
def setup_meta_kv_mode(meta: typing.MutableMapping):
    meta[predef.PredefParseKVMode] = False
    text = meta.get(predef.PredefKeyValueColumns, "")
    if text != "":
        columns = text.split(",")
        assert len(columns) >= 3
        meta[predef.PredefParseKVMode] = True
        meta[predef.PredefKeyColumn] = int(columns[0])
        meta[predef.PredefValueTypeColumn] = int(columns[1])
        meta[predef.PredefValueColumn] = int(columns[2])
        if len(columns) > 3:
            meta[predef.PredefCommentColumn] = int(columns[3])


# meta字段处理
def parse_meta_rows(sheet_rows: typing.Sequence) -> typing.Mapping:
    meta = {}
    for row in sheet_rows:
        if len(row) >= 2:
            key = row[0].strip()
            value = row[1].strip()
            if len(key) > 0 and len(value) > 0:
                meta[key] = value
    return meta


# 处理meta字段
def validated_meta(meta: typing.Mapping) -> typing.Mapping:
    if predef.OptionUniqueColumns in meta:
        field_names = meta[predef.OptionUniqueColumns].split(',')
        field_names = [v.strip() for v in field_names]
        meta[predef.OptionUniqueColumns] = field_names

    # default values
    if predef.PredefStructNameRow not in meta:
        meta[predef.PredefStructNameRow] = "1"  # 名称列
    if predef.PredefStructTypeRow not in meta:
        meta[predef.PredefStructTypeRow] = "2"  # 类型列
    if predef.PredefCommentRow not in meta:
        meta[predef.PredefCommentRow] = "3"  # 注释列
    if predef.PredefDataStartRow not in meta:
        meta[predef.PredefDataStartRow] = "4"  # 数据起始列
    return meta
