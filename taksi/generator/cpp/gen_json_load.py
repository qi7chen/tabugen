# Copyright (C) 2019-present prototyped.cn. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import taksi.descriptor.types as types
import taksi.descriptor.predef as predef
import taksi.descriptor.lang as lang
import taksi.descriptor.strutil as strutil
import taksi.generator.genutil as genutil
from taksi.generator.cpp.gen_header import CppStructGenerator


# C++ code generator
class CppJsonLoadGenerator(CppStructGenerator):
    TAB_SPACE = '    '

    @staticmethod
    def name():
        return "cpp-json"
