# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import pymysql
import util

class MySQLImporter:

    def __init__(self):
        self.options = []
        self.conn = None

    def name():
        return "pymysql"


    def initialize(self, argtext):
        self.options = util.parse_args(argtext)

        
    def make_conn(self):




    def import_all(self):
        pass


    def import_one(self):
        pass