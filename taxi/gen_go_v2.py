# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import codecs
import basegen
import predef
import util


# Go code generator, for SQL
class GoV2Generator(basegen.CodeGeneratorBase):

    def __init__(self):
        pass

    @staticmethod
    def name():
        return "go-v2"


    def gen_go_struct(self, struct, params):
        content = '// %s\n' % struct['comment']
        name = struct['camel_case_name']
        if 'prefix' in params:
            name = params['prefix'] + name
        content += 'type %s struct {\n' % name
        for field in struct['fields']:
            typename = go_type_mapping[field['type_name']]
            assert typename != "", field['type_name']
            content += '\t%s %s `json:"%s"`// %s\n' % (
            field['camel_case_name'], typename, field['name'], field['comment'])
        content += '}\n'
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
        if 'prefix' in params:
            name = params['prefix'] + name
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
        name = struct['camel_case_name']
        if 'prefix' in params:
            name = params['prefix'] + name
        content = 'func (p *%s) Load(rows *sql.Rows) error {\n' % name
        content += '\treturn rows.Scan('
        for i, field in enumerate(struct['fields']):
            content += '&p.%s' % field['camel_case_name']
            if i + 1 < len(struct['fields']):
                content += ', '
        content += ')\n}\n'
        return content

    # 生成insert语句
    def gen_insert_stmt_method(self, struct, params):
        name = struct['camel_case_name']
        if 'prefix' in params:
            name = params['prefix'] + name
        content = 'func (p *%s) InsertStmt() *storage.SqlOperation {\n' % name
        content += '\t return storage.NewSqlOperation("INSERT INTO `%s`(' % struct['name']
        mark = ''
        for i, field in enumerate(struct['fields']):
            mark += '?, '
            content += '`%s`' % field['name']
            if i + 1 < len(struct['fields']):
                content += ', '
        content += ') VALUES(%s)", ' % mark[:-2]
        clause = ''
        for field in struct['fields']:
            clause += 'p.%s, ' % field['camel_case_name']
        content += clause[:-2]
        content += ')\n}\n'
        return content


    # 生成update语句
    def gen_update_stmt_method(self, struct, params):
        name = struct['camel_case_name']
        if 'prefix' in params:
            name = params['prefix'] + name
        clause, keys = self.gen_where_clause(struct)
        assert len(clause) > 0, struct
        content = 'func (p *%s) UpdateStmt() *storage.SqlOperation {\n' % name
        content += '\t return storage.NewSqlOperation("UPDATE `%s` SET ' % struct['name']
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
                clause += 'p.%s, ' % field['camel_case_name']
        for field in struct['fields']:
            if field['name'] in keys:
                clause += 'p.%s, ' % field['camel_case_name']
        content += clause[:-2]
        content += ')\n}\n'
        return content


    # 生成delete语句
    def gen_remove_stamt_method(self, struct, params):
        name = struct['camel_case_name']
        if 'prefix' in params:
            name = params['prefix'] + name
        clause, keys = self.gen_where_clause(struct)
        assert len(clause) > 0, struct
        content = 'func (p *%s) DeleteStmt() *storage.SqlOperation {\n' % name
        content += '\t return storage.NewSqlOperation("DELETE FROM `%s`' % struct['name']
        content += clause
        content += '", '
        clause = ''
        for field in struct['fields']:
            if field['name'] in keys:
                clause += 'p.%s, ' % field['camel_case_name']
        content += clause[:-2]
        content += ')\n}\n'
        return content


    def run(self, descriptors, args):
        params = util.parse_args(args)
        content = '// This file is auto-generated by taxi v%s. DO NOT EDIT!\n\n' % util.version_string
        content += 'package %s\n\n' % params['pkg']
        content += 'import (\n'
        content += '\t"fatchoy/storage"\n'
        content += '\t"database/sql"\n'
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

        outdir = params.get(predef.OptionOutSourceDir, '.')
        filename = outdir + '/stub.go'
        f = codecs.open(filename, 'w', 'utf-8')
        f.writelines(content)
        f.close()
        print('wrote to %s' % filename)

        gopath = os.getenv('GOPATH')
        if gopath is not None:
            cmd = gopath + '/bin/goimports -w ' + filename
            print(cmd)
            os.system(cmd)


go_type_mapping = {
    'bool': 'bool',
    'int8': 'int8',
    'uint8': 'uint8',
    'int16': 'int16',
    'uint16': 'uint16',
    'int': 'int',
    'int32': 'int32',
    'uint32': 'uint32',
    'int64': 'int64',
    'uint64': 'uint64',
    'float': 'float32',
    'float32': 'float32',
    'float64': 'float64',
    'string': 'string',
    'bytes': '[]byte',
    'datetime': 'time.Time',
}