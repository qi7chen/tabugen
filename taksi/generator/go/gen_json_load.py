# Copyright (C) 2019-present prototyped.cn. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import codecs
import taksi.descriptor.types as types
import taksi.descriptor.predef as predef
import taksi.descriptor.lang as lang
import taksi.generator.genutil as genutil
import taksi.descriptor.strutil as strutil
import taksi.version as version
from taksi.generator.go.gen_struct import GoStructGenerator


# Go json load generator
class GoJsonLoadGenerator(GoStructGenerator):
    TAB_SPACE = '\t'

    @staticmethod
    def name():
        return "go-json"

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

    def run(self, descriptors, params):
        content = '// This file is auto-generated by TAKSi v%s, DO NOT EDIT!\n\n' % version.VER_STRING
        content += 'package %s\n' % params['pkg']
        content += self.gen_const_names(descriptors)

        for struct in descriptors:
            genutil.setup_comment(struct)
            genutil.setup_key_value_mode(struct)

        for struct in descriptors:
            content += self.generate(struct, params)

        filename = params.get(predef.OptionOutSourceFile, 'config.go')
        filename = os.path.abspath(filename)
        strutil.compare_and_save_content(filename, content, 'utf-8')
        print('wrote source to %s' % filename)

        goroot = os.getenv('GOROOT')
        if goroot is not None:
            cmd = goroot + '/bin/go fmt ' + filename
            print(cmd)
            os.system(cmd)
