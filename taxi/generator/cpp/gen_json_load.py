# Copyright (C) 2019-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import taxi.descriptor.types as types
import taxi.descriptor.predef as predef
import taxi.descriptor.lang as lang
import taxi.descriptor.strutil as strutil
import taxi.generator.genutil as genutil
from taxi.generator.cpp.gen_header import CppStructGenerator


# C++ code generator
class CppJsonLoadGenerator(CppStructGenerator):
    TAB_SPACE = '    '

    @staticmethod
    def name():
        return "cpp-json"