# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import csv
import codecs
import re
import json
import predef
import util

class CodeGeneratorBase:

    def __init__(self):
        pass

    # 根据'column_index'查找一个字段
    def get_field_by_column_index(self, struct, column_idx):
        assert column_idx > 0
        idx = 0
        for field in struct["fields"]:
            if field["column_index"] == column_idx:
                return idx, field
            idx += 1
        print(struct['fields'])
        assert False, column_idx

    # 获取字段
    def get_struct_keys(self, struct, keyname, keymapping):
        if keyname not in struct['options']:
            return []

        key_tuples = []
        column_keys = struct['options'][keyname].split(',')
        assert len(column_keys) > 0, struct['name']

        for column in column_keys:
            idx, field = self.get_field_by_column_index(struct, int(column))
            typename = keymapping(field['original_type_name'])
            name = field['name']
            key_tuples.append((typename, name))
        return key_tuples

    # 读取KV模式的字段
    def get_struct_kv_fields(self, struct):
        rows = struct["data-rows"]
        keycol = struct["options"][predef.PredefKeyColumn]
        valcol = struct["options"][predef.PredefValueColumn]
        typecol = int(struct['options'][predef.PredefValueTypeColumn])
        assert keycol > 0 and valcol > 0 and typecol > 0
        comment_idx = -1
        if predef.PredefCommentColumn in struct["options"]:
            commentcol = int(struct["options"][predef.PredefCommentColumn])
            assert commentcol > 0
            comment_field = {}
            comment_idx, comment_field = self.get_field_by_column_index(struct, commentcol)

        key_idx, key_field = self.get_field_by_column_index(struct, keycol)
        value_idx, value_field = self.get_field_by_column_index(struct, valcol)
        type_idx, type_field = self.get_field_by_column_index(struct, typecol)

        fields = []
        for i in range(len(rows)):
            # print(rows[i])
            name = rows[i][key_idx].strip()
            typename = rows[i][type_idx].strip()
            assert len(name) > 0, (rows[i], key_idx)
            comment = ''
            if comment_idx >= 0:
                comment = rows[i][comment_idx].strip()
            field = {
                'name': name,
                'camel_case_name': util.camel_case(name),
                'type_name': typename,
                'original_type_name': typename,
                'comment': comment,
            }
            fields.append(field)

        return fields

    # KV模式读取
    def setup_key_value_mode(self, struct):
        struct["options"][predef.PredefParseKVMode] = False
        kvcolumns = struct["options"].get(predef.PredefKeyValueColumn, "")
        if kvcolumns != "":
            kv = kvcolumns.split(",")
            assert len(kv) == 2
            struct["options"][predef.PredefParseKVMode] = True
            struct["options"][predef.PredefKeyColumn] = int(kv[0])
            struct["options"][predef.PredefValueColumn] = int(kv[1])

    # 注释
    def setup_comment(self, struct):
        comment = struct.get("comment", "")
        if comment == "":
            comment = struct["options"].get(predef.PredefClassComment, "")
            if comment != "":
                struct["comment"] = comment

    # 将数据写入csv文件
    def write_data_rows(self, struct, params):
        datadir = "."
        if predef.OptionOutDataDir in params:
            datadir = params[predef.OptionOutDataDir]

        # 置空不必要显示的内容
        rows = struct["data-rows"]
        if struct['options'][predef.PredefParseKVMode]:
            typecol = int(struct['options'][predef.PredefValueTypeColumn])
            commentcol = int(struct['options'][predef.PredefCommentColumn])
            for row in rows:
                row[typecol-1] = ''
                row[commentcol-1] = ''
        else:
            if predef.OptionHideColumns in params:
                text = struct["options"].get(predef.PredefHideColumns, "")
                text = text.strip()
                if len(text) > 0:
                    columns = [int(x.strip()) for x in text.split(',')]
                    for row in rows:
                        for idx in columns:
                            row[idx-1] = ''

        filename = "%s/%s.csv" % (datadir, struct['name'].lower())
        filename = os.path.abspath(filename)
        f = codecs.open(filename, "w", "utf-8")
        w = csv.writer(f)
        w.writerows(rows)
        f.close()
        print("wrote csv data to", filename)

    # 获取生成数组字段的范围
    def get_vec_field_range(self, struct, camel_case_name=False):
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

        name = util.common_prefix(names[0], names[1])
        assert len(name) > 0, struct["name"]
        name = re.sub("[0-9]", "", name)    # remove number char
        return names, name

    #
    def get_inner_class_range(self, struct):
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

    #内部嵌入的class
    def get_inner_class_fields(self, struct, camel_case_name=False):
        if predef.PredefInnerTypeRange not in struct["options"]:
            return [], []

        inner_class_type = struct["options"][predef.PredefInnerTypeClass]
        assert len(inner_class_type) > 0
        inner_class_name = struct["options"][predef.PredefInnerTypeName]
        assert len(inner_class_name) > 0

        start, end, step = self.get_inner_class_range(struct)
        fields = struct['fields']
        inner_fields = []
        for n in range(start, start + step):
            field = fields[n]
            content = json.dumps(field, allow_nan=False, ensure_ascii=False)  # use json to make a clone
            newobj = json.loads(content)
            newobj['name'] = util.remove_suffix_number(newobj['name'])
            inner_fields.append(newobj)

        field_names = []
        for n in range(start, end):
            field = fields[n]
            if camel_case_name:
                field_names.append(field["camel_case_name"])
            else:
                field_names.append(field["name"])

        return field_names, inner_fields