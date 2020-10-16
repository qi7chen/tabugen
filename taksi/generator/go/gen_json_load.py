# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import taksi.strutil as strutil
import taksi.predef as predef
import taksi.generator.genutil as genutil
import taksi.version as version
from taksi.generator.go.gen_struct import GoStructGenerator


# 生成Go加载JSON文件数据代码
class GoJsonLoadGenerator(GoStructGenerator):
    TAB_SPACE = '\t'

    def get_const_key_name(self, name):
        return 'Key%sName' % name

    def gen_const_names(self, descriptors):
        content = 'const (\n'
        for struct in descriptors:
            name = strutil.camel_to_snake(struct['name'])
            content += '\t%s = "%s"\n' % (self.get_const_key_name(struct['name']), name)
        content += ')\n\n'
        return content

    def generate(self, struct, params):
        content = ''
        content += self.gen_struct_define(struct, params)
        return content

