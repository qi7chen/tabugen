# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


from taksi.generator.cpp.gen_header import CppStructGenerator


# C++ code generator
class CppJsonLoadGenerator(CppStructGenerator):
    TAB_SPACE = '    '

    @staticmethod
    def name():
        return "cpp-json"

    def run(self, descriptors, params):
        # TO-DO: with no reflection support in C++, is it valuable to write JSON code?
        raise NotImplementedError
