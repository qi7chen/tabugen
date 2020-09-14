#!/usr/bin/env python3
#
# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import sys
import argparse
from taksi.version import VER_STRING
from taksi.registry import get_struct_parser, get_code_generator, get_data_transformer


def run(args):
    parser = get_struct_parser(args.parser)
    if parser is None:
        print('parser `%s` is not implemented' % args.parser)
        sys.exit(1)

    codegen = None
    input_tran = None
    output_tran = None
    if args.generator is not None:
        codegen = get_code_generator(args.generator)
        if codegen is None:
            print('code generator `%s` is not implemented' % args.generator)
            sys.exit(1)

    if args.input is not None:
        input_tran = get_data_transformer(args.input)
        if input_tran is None:
            print('data transformer `%s` is not implemented' % args.generator)
            sys.exit(1)

    if args.output is not None:
        output_tran = get_data_transformer(args.output)
        if output_tran is None:
            print('data transformer `%s` is not implemented' % args.generator)
            sys.exit(1)

    if codegen is None and input_tran is None and output_tran is None:
        print('no generator and input/output specified, nothing would happen')
        sys.exit(1)

    parser.init(args)
    descriptors = parser.parse_all()
    print(len(descriptors), 'file parsed')

    if len(descriptors) > 0:
        if codegen is not None:
            codegen.run(descriptors, args)
        if input_tran is not None:
            input_tran.run(descriptors, args)
        if output_tran is not None:
            output_tran.run(descriptors, args)
    else:
        print('no descriptor to generate')


def main():
    parser = argparse.ArgumentParser(description="A configuration import/export tool")
    parser.add_argument("-p", "--parser", help="where data description from(excel, mysql etc)")
    parser.add_argument("-g", "--generator", help="code generator name")
    parser.add_argument("-i", "--input", help="input data file(csv, json, xml etc)")
    parser.add_argument("-o", "--output", help="output data file(csv, json, xml etc)")
    parser.add_argument("-v", "--version", action='version', version=VER_STRING)

    # excel options
    parser.add_argument("--parse-files", help="files or directory to parse struct", default='.')
    parser.add_argument("--parse-meta-file", help="meta file to parse struct")
    parser.add_argument("--parse-file-skip", help="files or directory to skip in parsing struct")

    # mysql options
    parser.add_argument("--db-host", help="database host address", default="localhost")
    parser.add_argument("--db-port", help="database host port", default="3306")
    parser.add_argument("--db-user", help="database username")
    parser.add_argument("--db-password", help="database user password")
    parser.add_argument("--db-schema", help="database schema")
    parser.add_argument("--db-table", help="database table")

    parser.add_argument("--source-file-encoding", help="encoding of generated source file", default='utf-8')
    parser.add_argument("--data-file-encoding", help="encoding of output data file", default='utf-8')
    parser.add_argument("--source-file-out", help="output directory of generated source file", default='.')
    parser.add_argument("--data-file-out", help="output directory of output data file", default='.')
    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
