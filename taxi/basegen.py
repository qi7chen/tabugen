# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import csv
import codecs
import re
import predef
import util

class CodeGeneratorBase:

    def __init__(self):
        pass

    def get_field_by_column_index(self, struct, column_idx):
        assert column_idx > 0
        idx = 0
        for field in struct["fields"]:
            if field["column_index"] == column_idx:
                return idx, field
            idx += 1
        assert False


    #读取KV模式的字段
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


    #KV模式读取
    def setup_key_value_mode(self, struct):
        struct["options"][predef.PredefParseKVMode] = False
        kvcolumns = struct["options"].get(predef.PredefKeyValueColumn, "")
        if kvcolumns != "":
            kv = kvcolumns.split(",")
            assert len(kv) == 2
            struct["options"][predef.PredefParseKVMode] = True
            struct["options"][predef.PredefKeyColumn] = int(kv[0])
            struct["options"][predef.PredefValueColumn] = int(kv[1])


    def setup_comment(self, struct):
        comment = struct.get("comment", "")
        if comment == "":
            comment = struct["options"].get(predef.PredefClassComment, "")
            if comment != "":
                struct["comment"] = comment


    #将数据写入csv文件
    def write_data_rows(self, struct, args):
        datadir = "."
        if predef.OptionOutDataDir in args:
            datadir = args[predef.OptionOutDataDir]
        filename = "%s/%s.csv" % (datadir, struct['name'].lower())
        rows = struct["data-rows"]
        f = codecs.open(filename, "w", "utf-8")
        w = csv.writer(f)
        w.writerows(rows)
        f.close()
        print("wrote csv data to", filename)

    # 获取生成数组字段的范围
    def get_field_range(self, struct, camel_case_name=False):
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

        if len(names) == 0:
            return [], ""

        name = util.common_prefix(names)
        assert len(name) > 0, struct["name"]
        name = re.sub("[0-9]", "", name)    # remove number char
        return names, name