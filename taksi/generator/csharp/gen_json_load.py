# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import taksi.predef as predef
import taksi.strutil as strutil
import taksi.generator.genutil as genutil
import taksi.version as version
from taksi.generator.csharp.gen_struct import CSharpStructGenerator


# C# csv load generator
class CSharpJsonLoadGenerator(CSharpStructGenerator):
    TAB_SPACE = '    '

    @staticmethod
    def name():
        return "cs-json"

    def run(self, descriptors, params):
        content = '// This file is auto-generated by TAKSi v%s, DO NOT EDIT!\n\n' % version.VER_STRING
        content += 'using System;\n'
        content += 'using System.Collections.Generic;\n'

        if 'pkg' in params:
            content += '\nnamespace %s\n{\n' % params['pkg']

        for struct in descriptors:
            genutil.setup_comment(struct)
            genutil.setup_key_value_mode(struct)

        for struct in descriptors:
            content += self.gen_cs_struct(struct)
            content += '}\n\n'

        if 'pkg' in params:
            content += '\n}\n'  # namespace

        filename = params.get(predef.OptionOutSourceFile, 'AutogenConfig.cs')
        filename = os.path.abspath(filename)
        strutil.compare_and_save_content(filename, content, 'utf-8')
        print('wrote source file to', filename)
