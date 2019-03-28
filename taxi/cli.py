#!/usr/bin/env python3
#
# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import sys
import argparse
from taxi.registry import get_importer, get_generator
from taxi.version import VER_STRING


def run(args):
    generator = get_generator(args.generator)
    if generator is None:
        print('generator `%s` is not supported' % args.generator)
        sys.exit(1)

    importer = get_importer(args.mode)
    if importer is None:
        print('importer `%s` is not supported' % args.mode)
        sys.exit(1)

    importer.initialize(args.import_args)
    descriptors = importer.import_all()
    print(len(descriptors), 'file parsed')

    if len(descriptors) > 0:
        generator.run(descriptors, args.export_args)


def main():
    parser = argparse.ArgumentParser(description="Export game configuration to source code")
    parser.add_argument("-m", "--mode", help="mode of importer, mysql or excel", default="excel")
    parser.add_argument("-a", "--import-args", help="arguments of importer", default="")
    parser.add_argument("-g", "--generator", help="generator name", default="cpp")
    parser.add_argument("-e", "--export-args", help="arguments of exporter", default="")
    parser.add_argument("-v", "--version", action='store_true', help="show version string", default=False)
    args = parser.parse_args()

    if args.version:
        print("v" + VER_STRING)
        return

    run(args)


if __name__ == '__main__':
    main()
