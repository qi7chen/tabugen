#!/usr/bin/env python3
#
# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import argparse
import registry


def run(args):
    generator = registry.get_generator(args.generator)
    importer = registry.get_importer(args.mode)
    importer.initialize(args.import_args)
    descriptors = importer.import_all()
    generator.run(descriptors, args.export_args)


def main():
    parser = argparse.ArgumentParser(description="Export game configuration to source code")
    parser.add_argument("-m", "--mode", help="mode of importer, mysql or excel", default="excel")
    parser.add_argument("-i", "--import-args", help="arguments of importer", default="")
    parser.add_argument("-g", "--generator", help="generator name", default="cppv1")
    parser.add_argument("-e", "--export-args", help="arguments of exporter", default="")
    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()