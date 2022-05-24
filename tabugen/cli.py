#!/usr/bin/env python3
#
# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import argparse
import sys

from tabugen.registry import get_struct_parser, get_code_generator, get_data_writer
from tabugen.version import VER_STRING


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
        filepath = item[0]
        name = item[1]
        if filepath is not None:
            codegen = get_code_generator(name)
            if codegen is None:
                print('%s code generator is not implemented' % name.title())
                sys.exit(1)
            code_generators.append((codegen, filepath))

    if len(code_generators) == 0 and args.out_data_format is None:
        print('no code generation and data output, nothing would happen')
        sys.exit(1)

    parser.init(args)
    descriptors = parser.parse_all()
    print(len(descriptors), 'file parsed')

    if len(descriptors) > 0:
        for pair in code_generators:
            codegen = pair[0]
            filepath = pair[1]
            if args.gen_csv_parse:
                codegen.setup('csv')
            codegen.run(descriptors, filepath, args)

    if not args.without_data and args.out_data_format is not None:
        writer = get_data_writer(args.out_data_format)
        if writer is None:
            print('data writer %s not found' % args.out_data_format)
            sys.exit(1)
        writer.process(descriptors, args)


# 校验参数
def verify_args(args):
    if args.package is None:
        print('package name must be set')
        sys.exit(1)

    if args.array_delim is not None:
        if len(args.array_delim) != 1:
            print('array delimiter must contains 1 char!')
            sys.exit(1)

    if args.map_delims is not None:
        if len(args.map_delims) != 2:
            print('map delimiter must contains 2 char(s)!')
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="A configuration import/export and code generation tool")
    parser.add_argument("-v", "--version", action='version', version='v' + VER_STRING)
    parser.add_argument("--parser", default="excel", help="where your row data come from(excel, xml, database etc)")
    parser.add_argument("--without_data", action="store_true", help="parse struct definition but no data rows")

    # excel options
    parser.add_argument("--parse_files", help="files or directory for struct parsing")
    parser.add_argument("--parse_meta_file", help="meta file for struct parsing")
    parser.add_argument("--parse_file_skip", help="files or directory to skip in struct parsing")
    parser.add_argument("--skip_column", default='', help="skipping column when do parsing")
    parser.add_argument("--array_delim", default=",", help="array item delimiter")
    parser.add_argument("--map_delims", default=";=", help="map item delimiters")

    # source code options
    parser.add_argument("--config_manager_class", default='', help="name of auto-generated config manager class")
    parser.add_argument("--gen_csv_parse", action='store_true', help="also generator csv parse method code")
    parser.add_argument("--cpp_out", help="file path of generate C++ class source code")
    parser.add_argument("--go_out", help="file path of generate go struct source code")
    parser.add_argument("--csharp_out", help="file path of generate C# class source code")
    parser.add_argument("--java_out", help="file path of generate Java class source code")
    parser.add_argument("--package", default="config", help="name of generated source language package")
    parser.add_argument("--cpp_pch", help="C++ precompiled header file to include in source file")
    parser.add_argument("--go_json_tag", action="store_true", help="generate JSON tag for Go struct")
    parser.add_argument("--go_fmt", action="store_true", help="run go fmt on generated source file")

    # output options
    parser.add_argument("--extra_cpp_include", default="common/Conv.h", help="extra include C++ header")
    parser.add_argument("--source_file_encoding", default="utf8", help="encoding of generated source file")
    parser.add_argument("--data_file_encoding", default="utf8", help="encoding of output data file")
    parser.add_argument("--out_csv_delim", default=",", help="output CSV file field delimiter")
    parser.add_argument("--out_data_format", help="output data file format(CSV, JSON, XML etc")
    parser.add_argument("--out_data_path", default=".", help="output file path")
    parser.add_argument("--json_indent", action="store_true", help="enable JSON indent for output data")
    parser.add_argument("--json_snake_case", action="store_true", help="enable JSON field to be snake case")

    args = parser.parse_args()
    verify_args(args)
    run(args)
