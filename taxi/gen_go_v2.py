# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import basegen

# Go code generator, for SQL
class GoV2Generator(basegen.CodeGeneratorBase):

    def __init__(self):
        pass

    @staticmethod
    def name():
        return "gov2"