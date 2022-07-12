"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

import re
import typing

import tabugen.predef as predef
import tabugen.util.strutil as strutil


# 根据'column_index'查找一个字段
def get_field_by_column_index(struct, column_idx: int):
    assert column_idx > 0
    idx = 0
    for field in struct["fields"]:
        if field["column_index"] == column_idx:
            return idx, field
        idx += 1
    # print(struct['fields'])
    assert False, column_idx


# 获取字段
def get_struct_keys(struct, keyname: str, keymapping):
    if keyname not in struct['options']:
        return []

    key_tuples = []
    column_keys = struct['options'][keyname].split(',')
    assert len(column_keys) > 0, struct['name']

    for column in column_keys:
        idx, field = get_field_by_column_index(struct, int(column))
        typename = keymapping(field['original_type_name'])
        name = field['name']
        key_tuples.append((typename, name))
    return key_tuples


# 获取生成数组字段的范围
def get_vec_field_range(struct: typing.Mapping, camel_case_name=False) -> typing.Sequence:
    auto_vector = struct["options"].get(predef.OptionAutoVector, "off")
    if auto_vector == "off":
        return [], ""

    names = []
    field_type = None
    for field in struct["fields"]:
        if field.get("is_vector", False):
            if field_type is None:
                field_type = field["original_type_name"]
            else:
                assert field_type == field["original_type_name"]
            if camel_case_name:
                names.append(field["camel_case_name"])
            else:
                names.append(field["name"])

    if len(names) < 2:
        return [], ""

    name = strutil.find_common_prefix(names[0], names[1])
    assert len(name) > 0, struct["name"]
    name = re.sub("[0-9]", "", name)  # remove number char
    return names, name


#
def get_inner_class_range(struct):
    if predef.PredefInnerTypeRange not in struct["options"]:
        return 0, 0, 0

    text = struct["options"].get(predef.PredefInnerTypeRange, "")
    text = text.strip()
    if len(text) == 0:
        return 0, 0, 0

    numbers = [int(x) for x in text.split(',')]
    assert len(numbers) == 3

    fields = struct['fields']
    start = numbers[0] - 1
    assert start > 0, text
    end = numbers[1]
    if end < 0:
        end = len(fields)
    else:
        end += 1
    step = numbers[2]
    assert step >= 1, numbers

    assert (end - start) >= step, text
    assert (end - start) % step == 0, text

    return start, end, step


# 内部嵌入的class
def get_inner_class_struct_fields(struct):
    if predef.PredefInnerTypeRange not in struct["options"]:
        return []

    inner_class_type = struct["options"][predef.PredefInnerTypeClass]
    assert len(inner_class_type) > 0
    inner_class_name = struct["options"][predef.PredefInnerTypeName]
    assert len(inner_class_name) > 0

    start, end, step = get_inner_class_range(struct)
    fields = struct['fields']
    inner_fields = []
    for n in range(start, start + step):
        field = fields[n]
        new_field = {
            'type': field['type'],
            'type_name': field['type_name'],
            'original_type_name': field['original_type_name'],
            'comment': field['comment'],
            'name': strutil.remove_suffix_number(field['name']),
            'camel_case_name': strutil.remove_suffix_number(field['camel_case_name']),
        }
        inner_fields.append(new_field)

    return inner_fields


# 所有嵌入类的字段
def get_inner_class_mapped_fields(struct, camel_case_name=False):
    if predef.PredefInnerTypeRange not in struct["options"]:
        return [], []

    inner_class_type = struct["options"][predef.PredefInnerTypeClass]
    assert len(inner_class_type) > 0
    inner_class_name = struct["options"][predef.PredefInnerTypeName]
    assert len(inner_class_name) > 0

    field_names = []
    fields = []
    start, end, step = get_inner_class_range(struct)
    for n in range(start, end):
        field = struct['fields'][n]
        fields.append(field)
        if camel_case_name:
            field_names.append(field["camel_case_name"])
        else:
            field_names.append(field["name"])

    return field_names, fields


#
def enabled_fields(struct):
    fields = []
    for field in struct["fields"]:
        if field["enable"]:
            fields.append(field)
    return fields
