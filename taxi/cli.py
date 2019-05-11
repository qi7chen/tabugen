#!/usr/bin/env python3
#
# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import sys
import argparse
from taxi.registry import *
from taxi.version import VER_STRING
import taxi.descriptor.strutil as strutil


def run(args):
    importer = get_importer(args.mode)
    if importer is None:
        print('importer `%s` is not supported' % args.mode)
        sys.exit(1)

    codegen = None
    datagen = None
    if len(args.generator) > 0:
        codegen = get_code_generator(args.generator)
        if codegen is None:
            print('code generator `%s` is not supported' % args.generator)
            sys.exit(1)

    if len(args.output_format):
        datagen = get_data_generator(args.output_format)
        if datagen is None:
            print('data generator `%s` is not supported' % args.generator)
            sys.exit(1)

    if codegen is None and datagen is None:
        print('no generator specified, nothing would happen')
        sys.exit(1)

    import_args = strutil.parse_args(args.import_args)
    importer.initialize(import_args)
    descriptors = importer.import_all()
    print(len(descriptors), 'file parsed')

    export_args = strutil.parse_args(args.export_args)
    if len(descriptors) > 0:
        if codegen is not None:
            codegen.run(descriptors, export_args)
        if datagen is not None:
            datagen.run(descriptors, export_args)
    else:
        print('no descriptor to generate')


def main():
    parser = argparse.ArgumentParser(description="Export game configuration to source code")
    parser.add_argument("-m", "--mode", help="mode of importer, mysql or excel", default="excel")
    parser.add_argument("-a", "--import-args", help="arguments of importer", default="")
    parser.add_argument("-g", "--generator", help="code generator name", default="")
    parser.add_argument("-o", "--output-format", help="output data format(csv, json)", default="csv")
    parser.add_argument("-e", "--export-args", help="arguments of exporter", default="")
    parser.add_argument("-v", "--version", action='store_true', help="show version string", default=False)
    args = parser.parse_args()

    if args.version:
        print("v" + VER_STRING)
        return

    run(args)


if __name__ == '__main__':
    main()
