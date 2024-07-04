<#
# Copyright (C) 2023-present ichenq@outlook.com. All rights reserved.
#>

$CURRENT_DIR = Get-Location
$ROOT_DIR = Resolve-Path "../../"
$DATASHEET_DIR = Resolve-Path "../datasheet"
$OUT_SRC_DIR = Join-Path $CURRENT_DIR  "src"
$OUT_DATA_DIR = Join-Path $DATASHEET_DIR  "/res"

$Env:PYTHONPATH=$ROOT_DIR

Function Generate {
    python $ROOT_DIR/tabugen/__main__.py --file_asset=$DATASHEET_DIR --cpp_out=$OUT_SRC_DIR/Config --package=config --gen_csv_parse --source_file_encoding=utf_8_sig --out_data_path=$OUT_DATA_DIR --out_data_format=csv
    python $ROOT_DIR/tabugen/__main__.py --file_asset=$DATASHEET_DIR --out_data_path=$OUT_DATA_DIR --out_data_format=json --json_indent
}

# 需要先安装vcpkg，再通过vcpkg安装boost
Function RunTest {
    rm cmake-build -r -fo
    md cmake-build
    cd cmake-build

    cmake -B . -S .. "-DCMAKE_TOOLCHAIN_FILE=D:/App/vcpkg/scripts/buildsystems/vcpkg.cmake"
    cmake --build .
    cmake-build/Debug/tabugencpp
}

Generate
# RunTest

