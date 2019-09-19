# Copyright (C) 2018-present prototyped.cn. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import codecs
import taxi.descriptor.predef as predef
import taxi.descriptor.lang as lang
import taxi.descriptor.strutil as strutil
import taxi.generator.genutil as genutil
import taxi.version as version


# Go code generator, for SQL
class GoSqlOrmGenerator():

    def __init__(self):
        pass

    @staticmethod
    def name():
        return "go-v2"

    def gen_getset(self, struct, params):
        is_camelcase_field = params.get(predef.OptionCamelcaseField, "") != "off"
        name = struct['camel_case_name']
        name = params.get(predef.OptionNamePrefix, "") + name

        content = ''
        for field in struct['fields']:
            typename = lang.map_go_raw_type(field['type_name'])
            # getter
            if not is_camelcase_field:
                content += 'func (m *%s) %s() %s {\n' % (name, field['camel_case_name'], typename)
                content += '    return %s' % field['name']
                content += '}\n'

            # setter
            content += 'func (m *%s) Set%s(v %s) {\n' % (name, field['camel_case_name'], typename)
            if is_camelcase_field:
                content += '    m.%s = v' % field['camel_case_name']
            else:
                content += '    m.%s = v' % field['name']
            content += '}\n'
        return content

    def gen_go_struct(self, struct, params):
        content = '// %s\n' % struct['comment']
        name = struct['camel_case_name']
        name = params.get(predef.OptionNamePrefix, "") + name
        is_camelcase_field = params.get(predef.OptionCamelcaseField, "") != "off"

        content += 'type %s struct {\n' % name
        for field in struct['fields']:
            typename = lang.map_go_raw_type(field['type_name'])
            assert typename != "", field['type_name']
            if is_camelcase_field:
                name = field['camel_case_name']
                content += '\t%s %s `json:"%s"`// %s\n' % (name, typename, field['name'], field['comment'])
            else:
                name = field['name']
                content += '\t%s %s // %s\n' % (name, typename, field['comment'])
        content += '}\n'

        # getter and setter
        opt = params.get(predef.OptionFieldGetterSetter, "")
        if opt != "off":
            content += self.gen_getset(struct, params)

        return content

    # 生成where语句后缀
    def gen_where_clause(self, struct):
        content = ''
        keys = []
        primary_keys = struct['options'].get('primary_keys', [])
        if len(primary_keys) > 0:
            content += ' WHERE `%s`=?' % primary_keys[0]
            keys.append(primary_keys[0])
        else:
            unique_keys = struct['options'].get('unique_keys', [])
            print('unique keys: ', unique_keys)
            if len(unique_keys) > 0:
                content += " WHERE "
                for i, key in enumerate(unique_keys):
                    keys.append(key)
                    content += '`%s`=?' % key
                    if i + 1 < len(unique_keys):
                        content += ' AND '
        return content, keys

    # 生成select语句
    def gen_select_stmt_variable(self, struct, params):
        clause, keys = self.gen_where_clause(struct)
        name = struct['camel_case_name']
        name = params.get(predef.OptionNamePrefix, "") + name

        content = '\tconst Sql%sStmt = "SELECT ' % name
        for i, field in enumerate(struct['fields']):
            content += '`%s`' % field['name']
            if i + 1 < len(struct['fields']):
                content += ', '
        content += ' FROM `%s`' % struct['name']
        if 'auto-select' in params:
            content += clause
        content += '"\n\n'
        return content

    # 生成Load方法
    def gen_load_method(self, struct, params):
        is_camelcase_field = params.get(predef.OptionCamelcaseField, "") != "off"
        name = struct['camel_case_name']
        name = params.get(predef.OptionNamePrefix, "") + name

        content = 'func (p *%s) Load(rows *sql.Rows) error {\n' % name
        content += '\treturn rows.Scan('
        for i, field in enumerate(struct['fields']):
            if is_camelcase_field:
                content += '&p.%s' % field['camel_case_name']
            else:
                content += '&p.%s' % field['name']
            if i + 1 < len(struct['fields']):
                content += ', '
        content += ')\n}\n'
        return content

    # 生成insert语句
    def gen_insert_stmt_method(self, struct, params):
        is_camelcase_field = params.get(predef.OptionCamelcaseField, "") != "off"
        name = struct['camel_case_name']
        name = params.get(predef.OptionNamePrefix, "") + name

        content = 'func (p *%s) InsertStmt() *storage.DBOperation {\n' % name
        content += '\t return storage.NewDBOperation("INSERT INTO `%s`(' % struct['name']
        mark = ''
        for i, field in enumerate(struct['fields']):
            mark += '?, '
            content += '`%s`' % field['name']
            if i + 1 < len(struct['fields']):
                content += ', '
        content += ') VALUES(%s)", ' % mark[:-2]
        clause = ''
        for field in struct['fields']:
            if is_camelcase_field:
                clause += 'p.%s, ' % field['camel_case_name']
            else:
                clause += 'p.%s, ' % field['name']
        content += clause[:-2]
        content += ')\n}\n'
        return content

    # 生成update语句
    def gen_update_stmt_method(self, struct, params):
        is_camelcase_field = params.get(predef.OptionCamelcaseField, "") != "off"
        name = struct['camel_case_name']
        name = params.get(predef.OptionNamePrefix, "") + name

        clause, keys = self.gen_where_clause(struct)
        assert len(clause) > 0, struct
        content = 'func (p *%s) UpdateStmt() *storage.DBOperation {\n' % name
        content += '\t return storage.NewDBOperation("UPDATE `%s` SET ' % struct['name']
        for i, field in enumerate(struct['fields']):
            if field['name'] not in keys:
                content += '`%s`=?' % field['name']
                if i + 1 < len(struct['fields']):
                    content += ', '
        content += clause
        content += '",'
        clause = ''
        for field in struct['fields']:
            if field['name'] not in keys:
                if is_camelcase_field:
                    clause += 'p.%s, ' % field['camel_case_name']
                else:
                    clause += 'p.%s, ' % field['name']
        for field in struct['fields']:
            if field['name'] in keys:
                if is_camelcase_field:
                    clause += 'p.%s, ' % field['camel_case_name']
                else:
                    clause += 'p.%s, ' % field['name']
        content += clause[:-2]
        content += ')\n}\n'
        return content

    # 生成delete语句
    def gen_remove_stamt_method(self, struct, params):
        is_camelcase_field = params.get(predef.OptionCamelcaseField, "") != "off"
        name = struct['camel_case_name']
        name = params.get(predef.OptionNamePrefix, "") + name

        clause, keys = self.gen_where_clause(struct)
        assert len(clause) > 0, struct
        content = 'func (p *%s) DeleteStmt() *storage.DBOperation {\n' % name
        content += '\t return storage.NewDBOperation("DELETE FROM `%s`' % struct['name']
        content += clause
        content += '", '
        clause = ''
        for field in struct['fields']:
            if field['name'] in keys:
                if is_camelcase_field:
                    clause += 'p.%s, ' % field['camel_case_name']
                else:
                    clause += 'p.%s, ' % field['name']
        content += clause[:-2]
        content += ')\n}\n'
        return content

    def run(self, descriptors, args):
        params = strutil.parse_args(args)
        content = '// This file is auto-generated by taxi v%s. DO NOT EDIT!\n\n' % version.VER_STRING
        content += 'package %s\n\n' % params['pkg']
        content += 'import (\n'
        content += '\t"database/sql"\n'
        content += '\t"fatchoy/storage"\n'
        content += '\t"strconv"\n'
        content += ')\n\n'

        for struct in descriptors:
            content += self.gen_go_struct(struct, params)
            content += '\n'
            content += self.gen_select_stmt_variable(struct, params)
            content += '\n'
            content += self.gen_load_method(struct, params)
            content += '\n'
            content += self.gen_insert_stmt_method(struct, params)
            content += '\n'
            content += self.gen_update_stmt_method(struct, params)
            content += '\n'
            content += self.gen_remove_stamt_method(struct, params)

        filename = params.get(predef.OptionOutSourceFile, 'stub.go')
        f = codecs.open(filename, 'w', 'utf-8')
        f.writelines(content)
        f.close()
        print('wrote source to %s' % filename)

        gopath = os.getenv('GOPATH')
        if gopath is not None:
            cmd = gopath + '/bin/goimports -w ' + filename
            print(cmd)
            os.system(cmd)


