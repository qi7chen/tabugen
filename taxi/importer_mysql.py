# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import pymysql
import unittest
import descriptor
import util


class MySQLImporter:

    def __init__(self):
        self.options = []
        self.tables = []
        self.conn = None

    @staticmethod
    def name():
        return "mysql"


    def initialize(self, argtext):
        options = util.parse_args(argtext)
        self.make_conn(options)
        if "db" not in options:
            for name in self.get_database_names():
                self.tables = self.get_all_table_status(name)
        else:
            self.tables = self.get_all_table_status(options["db"])


    def make_conn(self, opt):
        host = opt.get("host", "localhost")
        port = int(opt.get("port", "3306"))
        db = opt.get("db", "")
        user = opt["user"]
        passwd = opt["passwd"]
        conn = pymysql.connect(host=host, user=user, port=port, password=passwd, db=db, charset="utf8")
        self.conn = conn


    def query_stmt(self, stmt):
        cur = self.conn.cursor()
        cur.execute(stmt)
        rows = cur.fetchall()
        cur.close()
        self.conn.commit()
        return rows


    def get_database_names(self):
        names = []
        ignored_name = ["information_schema", "performance_schema", "mysql", "sys"]
        for row in self.query_stmt("SHOW DATABASES"):
            name = row[0]
            if name not in ignored_name:
                names.append(name)
        return names


    def get_all_table_status(self, schema):
        tables = []
        self.query_stmt("USE `%s`;" % schema)
        for row in self.query_stmt("SHOW TABLES;"):
            status = {"schema": schema}
            for row in self.query_stmt("SHOW TABLE STATUS LIKE '%s'" % row[0]):
                status["name"] = row[0]
                # status["engine"] = row[1]
                # status["version"] = row[2]
                # status["row_format"] = row[3]
                # status["rows"] = row[4]
                # status["avg_row_len"] = row[5]
                # status["data_len"] = row[6]
                # status["max_data_len"] = row[7]
                # status["index_len"] = row[8]
                # status["data_free"] = row[9]
                # status["auto_incr"] = row[10]
                # status["create_time"] = str(row[11])
                # status["update_time"] = row[12]
                # status["check_time"] = row[13]
                # status["collation"] = row[14]
                # status["checksum"] = row[15]
                # status["create_options"] = row[16]
                status["comment"] = row[17]
            tables.append(status)
        return tables


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


    def import_all(self):
        descriptors = []
        for status in self.tables:
            struct = self.import_one(status)
            print(struct)
            descriptors.append(struct)
        return descriptors


    def import_one(self, status):
        self.query_stmt("USE `%s`;" % status["schema"])
        name = status["name"]
        struct = {
            "name": status["name"],
            "comment": status["comment"],
            "camel_case_name": util.camel_case(status["name"]),
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
            field["camel_case_name"] = util.camel_case(field["name"])
            field["type_name"] = type_name
            field["type"] = descriptor.get_type_by_name(type_name)

            key = column.get("key", "")
            if key == "PRI":
                primary_keys.append(column["name"])
            if key == "UNI":
                unique_keys.append(column["name"])
            if key == "MUL":
                index_keys.append(column["name"])

            if prev_field is not None and util.is_vector_fields(prev_field, field):
                prev_field["is_vector"] = True
                field["is_vector"] = True
            prev_field = field

            fields.append(field)

        options["primary_keys"] = ','.join(primary_keys)
        options["unique_keys"] = ','.join(unique_keys)
        options["index_keys"] = ','.join(index_keys)
        struct["options"] = options
        struct["fields"] = fields
        return struct



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
        args = "user=devel,passwd=r026^p0Y1Xa,db=choy_battle"
        importer = MySQLImporter()
        importer.initialize(args)
        importer.import_all()


if __name__ == '__main__':
    unittest.main()
