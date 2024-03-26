#!/usr/bin/env python3

# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


import argparse
import sys

import tabugen.util.helper as helper
from tabugen.registry import get_struct_parser, get_code_generator, get_data_writer
from tabugen.version import VER_STRING


valid_delimiters = [':', ',', '|', '=']


def run(args):
    parser = get_struct_parser('excel')

    pairs = [
        (args.cpp_out, 'cpp'),
        (args.go_out, 'go'),
        (args.cs_out, 'csharp'),
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
            if args.with_csv_parse:
                codegen.enable_gen_parse('csv')
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
    if args.delim2 == args.delim1:
        print('delim1 and delim2 must be different')
        sys.exit(1)
    if args.delim1 in valid_delimiters:
        helper.Delim1 = args.delim1
    if args.delim2 in valid_delimiters:
        helper.Delim2 = args.delim2


def main():
    parser = argparse.ArgumentParser(description="一个根据表格生成代码和配置转换的工具")
    parser.add_argument("-v", "--version", action='version', version='v' + VER_STRING)
    parser.add_argument("--without_data", action="store_true", help="只生成类型定义")
    parser.add_argument("--asset_path", help="文件名或者文件夹路径")
    parser.add_argument("--skip_files", help="需要跳过解析的文件名列表")
    parser.add_argument("--legacy", action='store_true', help="兼容模式")
    parser.add_argument("--project_kind", default='', help="指定包含此前缀的名称才纳入解析")
    parser.add_argument("--delim1", default=",", help="map和array的分隔符")
    parser.add_argument("--delim2", default=":", help="map的kv分隔符")
    parser.add_argument("--with_csv_parse", action='store_true', help="生成csv读取代码")
    parser.add_argument("--with_conv", action='store_true', help="生成用于解析字符串的工具代码")
    parser.add_argument("--cpp_out", help="指定生成C++代码的文件名")
    parser.add_argument("--go_out", help="指定生成Go代码的路径")
    parser.add_argument("--cs_out", help="指定生成C#代码的路径")
    parser.add_argument("--java_out", help="指定生成Java代码的路径")
    parser.add_argument("--package", default="config", help="指定命名空间或者包名")
    parser.add_argument("--cpp_pch", help="指定C++包含的预编译头")
    parser.add_argument("--extra_cpp_includes", default="", help="额外包含的C++头文件")
    parser.add_argument("--go_fmt", action="store_true", help="生成Go代码后执行go fmt")

    # output options
    parser.add_argument("--source_file_encoding", default="utf8", help="生成代码的文件编码格式")
    parser.add_argument("--data_file_encoding", default="utf8", help="导出数据的文件编码格式")
    parser.add_argument("--out_data_format", help="导出数据的格式(csv,json)")
    parser.add_argument("--out_data_path", default=".", help="导出数据文件的路径")
    parser.add_argument("--json_indent", action="store_true", help="导出的JSON使用缩进格式")
    parser.add_argument("--json_snake_case", action="store_true", help="导出的JSON使用snake_case")

    args = parser.parse_args()
    verify_args(args)
    run(args)


if __name__ == '__main__':
    main()
