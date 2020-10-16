#!/usr/bin/env python3
#
# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import sys
import argparse
from taksi.version import VER_STRING
from taksi.registry import get_struct_parser, get_code_generator, get_data_writer


def run(args):
    parser = get_struct_parser(args.parser)
    if parser is None:
        print('struct parser `%s` not implemented' % args.parser)
        sys.exit(1)

    pairs = [
        (args.cpp_out, 'cpp'),
        (args.go_out, 'go'),
        (args.csharp_out, 'csharp'),
        (args.java_out, 'java'),
    ]
    code_generators = []
    for item in pairs:
        name = item[1]
        if item[0]:
            codegen = get_code_generator(name)
            if codegen is None:
                print('%s code generator is not implemented' % name.title())
                sys.exit(1)
            codegen.init(args.load_code_generator)
            code_generators.append(codegen)

    if len(code_generators) == 0:
        print('no code nothing would happen')
        sys.exit(1)

    parser.init(args)
    descriptors = parser.parse_all()
    print(len(descriptors), 'file parsed')

    if len(descriptors) > 0:
        for codegen in code_generators:
            codegen.run(descriptors, args)

    if not args.without_data and args.out_data_format is not None:
        writer = get_data_writer(args.out_data_format)
        if writer is None:
            print('data writer %s not found' % args.out_data_format)
            sys.exit(1)
        writer.process(descriptors, args)


# 校验参数
def verify_args(args):
    if args.array_delim is not None:
        if len(args.array_delim) != 1:
            print('array delimiter must 1 char')
            sys.exit(1)

    if args.map_delims is not None:
        if len(args.map_delims) != 2:
            print('map delimiter must 2 char(s)')
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="A configuration import/export and code generation tool")
    parser.add_argument("-v", "--version", action='version', version=VER_STRING)
    parser.add_argument("--parser", help="where data description from(excel, mysql etc)")
    parser.add_argument("--without_data", action="store_true", help="parse struct definition but no data rows")

    # excel options
    parser.add_argument("--parse_files", help="files or directory for struct parsing")
    parser.add_argument("--parse_meta_file", help="meta file for struct parsing")
    parser.add_argument("--parse_file_skip", help="files or directory to skip in struct parsing")
    parser.add_argument("--array_delim", default=",", help="array item delimiter")
    parser.add_argument("--map_delims", default=",=", help="map item delimiter")

    # mysql options
    parser.add_argument("--db_host", help="database host address", default="localhost")
    parser.add_argument("--db_port", help="database host port", default="3306")
    parser.add_argument("--db_user", help="database username")
    parser.add_argument("--db_password", help="database user password")
    parser.add_argument("--db_schema", help="database schema")
    parser.add_argument("--db_table", help="database table")

    # source code options
    parser.add_argument("--cpp_out", action="store_true", help="generate C++ class definition code")
    parser.add_argument("--go_out", action="store_true", help="generate go struct definition code")
    parser.add_argument("--csharp_out", action="store_true", help="generate C# class definition code")
    parser.add_argument("--java_out", action="store_true", help="generate Java class definition code")
    parser.add_argument("--load_code_generator", help="name of generated source language package")
    parser.add_argument("--package", default="config", help="name of generated source language package")
    parser.add_argument("--cpp_pch", help="C++ precompiled header file to include in source file")

    # output options
    parser.add_argument("--source_file_encoding", help="encoding of generated source file", default='utf-8')
    parser.add_argument("--data_file_encoding", help="encoding of output data file", default='utf-8')
    parser.add_argument("--out_source_path", help="output file path of generated source")
    parser.add_argument("--out_csv_delim", default=";", help="output csv file field delimiter")
    parser.add_argument("--out_data_format", help="output data file format(csv, json, xml etc")
    parser.add_argument("--out_data_path", default=".", help="output file path of output data")

    args = parser.parse_args()
    verify_args(args)
    run(args)


if __name__ == '__main__':
    main()
