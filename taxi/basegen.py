# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import csv
import codecs
import predef

class CodeGeneratorBase:

    def __init__(self):
        pass

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


    def write_data_rows(self, struct, args):
        datadir = "./"
        if predef.OptionOutDataDir in args:
            datadir = args[predef.OptionOutDataDir]
        filename = "%s/%s.csv" % (datadir, struct['name'].lower())
        rows = struct["data-rows"]
        f = codecs.open(filename, "w", "utf-8")
        w = csv.writer(f)
        w.writerows(rows)
        f.close()