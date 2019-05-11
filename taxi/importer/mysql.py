# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import pymysql
import unittest
import taxi.descriptor.types as types
import taxi.descriptor.strutil as strutil


class MySQLImporter:

    def __init__(self):
        self.options = []
        self.tables = []
        self.conn = None

    @staticmethod
    def name():
        return "mysql"

    def initialize(self, args):
        options = args
        self.make_conn(options)
        if "db" not in options:
            for name in self.get_database_names():
                tables = self.get_all_table_status(name, '')
                self.tables += tables
        else:
            tablename = options.get('table', '')
            self.tables = self.get_all_table_status(options['db'], tablename)

    # 建立数据库连接
    def make_conn(self, opt):
        host = opt.get("host", "localhost")
        port = int(opt.get("port", "3306"))
        db = opt.get("db", "")
        user = opt["user"]
        passwd = opt["passwd"]
        conn = pymysql.connect(host=host, user=user, port=port, password=passwd, db=db, charset="utf8")
        self.conn = conn

    # 执行查询
    def query_stmt(self, stmt):
        cur = self.conn.cursor()
        cur.execute(stmt)
        rows = cur.fetchall()
        cur.close()
        self.conn.commit()
        return rows

    # 遍历数据库名称
    def get_database_names(self):
        names = []
        ignored_name = ["information_schema", "performance_schema", "mysql", "sys"]
        for row in self.query_stmt("SHOW DATABASES"):
            name = row[0]
            if name not in ignored_name:
                names.append(name)
        return names

    # 遍历所有table信息
    def get_all_table_status(self, schema, tablename):
        tables = []
        names = []

        self.query_stmt("USE `%s`;" % schema)

        if len(tablename) > 0:
            names.append(tablename)
        else:
            for row in self.query_stmt("SHOW TABLES;"):
                name = row[0]
                names.append(name)

        for name in names:
            info = {"schema": schema}
            for row in self.query_stmt("SHOW TABLE STATUS LIKE '%s'" % name):
                info["name"] = row[0]
                # info["engine"] = row[1]
                # info["version"] = row[2]
                # info["row_format"] = row[3]
                # info["rows"] = row[4]
                # info["avg_row_len"] = row[5]
                # info["data_len"] = row[6]
                # info["max_data_len"] = row[7]
                # info["index_len"] = row[8]
                # info["data_free"] = row[9]
                # info["auto_incr"] = row[10]
                # info["create_time"] = str(row[11])
                # info["update_time"] = row[12]
                # info["check_time"] = row[13]
                # info["collation"] = row[14]
                # info["checksum"] = row[15]
                # info["create_options"] = row[16]
                info["comment"] = row[17]
            tables.append(info)
        return tables

    # 遍历table的column信息
    def get_table_column_status(self, name):
        columns = []
        for row in self.query_stmt("SHOW FULL COLUMNS FROM " + name):
            column = {}
            column["name"] = row[0]
            column["original_type_name"] = row[1]
            column["collation"] = row[2]
            column["key"] = row[4]
            column["comment"] = row[8]
            columns.append(column)
        return columns

    # 导入所有
    def import_all(self):
        descriptors = []
        for info in self.tables:
            struct = self.import_one(info)
            # print(struct)
            descriptors.append(struct)
        return descriptors

    # 导入一个table
    def import_one(self, table):
        self.query_stmt("USE `%s`;" % table["schema"])
        name = table["name"]
        struct = {
            "name": table["name"],
            "comment": table["comment"],
            "camel_case_name": strutil.camel_case(table["name"]),
            "source": table["schema"],
        }
        options = {}
        primary_keys = []
        unique_keys = []
        index_keys = []
        fields = []
        prev_field = None
        for column in self.get_table_column_status(name):
            field = {
                "name": column["name"],
                "comment": column["comment"],
                "is_vector": False,
                "original_type_name": column["original_type_name"],
            }
            type_name = convert_mysql_type(field["original_type_name"])
            field["camel_case_name"] = strutil.camel_case(field["name"])
            field["type_name"] = type_name
            field["type"] = types.get_type_by_name(type_name)

            key = column.get("key", "")
            if key == "PRI":
                primary_keys.append(column["name"])
            if key == "UNI":
                unique_keys.append(column["name"])
            if key == "MUL":
                index_keys.append(column["name"])

            if prev_field is not None and strutil.is_vector_fields(prev_field, field):
                prev_field["is_vector"] = True
                field["is_vector"] = True
            prev_field = field

            fields.append(field)

        options["primary_keys"] = primary_keys
        options["unique_keys"] = unique_keys
        options["index_keys"] = index_keys
        struct["options"] = options
        struct["fields"] = fields
        return struct

# 数据库字段类型转换为编程语言识别类型
def convert_mysql_type(name):
    name = name.lower()
    if name.startswith("tinyint"):
        if name.startswith("tinyint(1)"):
            return "bool"
        if name.find("unsigned") > 0:
            return "uint8"
        return "int8"
    elif name.startswith("smallint"):
        if name.find("unsigned") > 0:
            return "uint16"
        return "int16"
    elif name.startswith("mediumint") or name.startswith("int"):
        if name.find("unsigned") > 0:
            return "uint32"
        return "int32"
    elif name.startswith("bigint"):
        if name.find("unsigned") > 0:
            return "uint64"
        return "int64"
    elif name.startswith("float"):
        return "float32"
    elif name.startswith("double") or name.startswith("decimal"):
        return "float64"
    elif name.startswith("blob") or name.startswith("binary"):
        return "bytes"
    elif name.startswith("date") or name.startswith("time"):    # datetime, timestamp
        return "datetime"
    elif name.startswith("char") or name.startswith("varchar") or name.startswith("text") or name.startswith("json"):
        return "string"
    else:
        assert False, name  # unsupported MySQL type


class TestMySQLImporter(unittest.TestCase):

    def test_parse_args(self):
        args = "user=devel,passwd=r026^p0Y1Xa,db=test"
        importer = MySQLImporter()
        importer.initialize(args)
        importer.import_all()


if __name__ == '__main__':
    unittest.main()
