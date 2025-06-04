<#
# Copyright (C) 2023-present qi7chen@github. All rights reserved.
#>

$CURRENT_DIR = Get-Location
$ROOT_DIR = Resolve-Path "../../"
$DATASHEET_DIR = Resolve-Path "../datasheet"
$OUT_SRC_DIR = Join-Path $CURRENT_DIR  "src"
$OUT_DATA_DIR = Join-Path $DATASHEET_DIR  "/res"

$Env:PYTHONPATH=$ROOT_DIR

Function Generate {
    python $ROOT_DIR/tabugen/__main__.py --file_asset=$DATASHEET_DIR --package=config --cpp_out=$OUT_SRC_DIR/Config --source_file_encoding=utf_8_sig --out_data_path=$OUT_DATA_DIR --out_data_format=csv  --gen_csv_parse --extra_cpp_includes='strconv.h'
    python $ROOT_DIR/tabugen/__main__.py --file_asset=$DATASHEET_DIR --out_data_path=$OUT_DATA_DIR --out_data_format=json --json_indent
}

# 需要先安装vcpkg
Function RunTest {
    rm cmake-build -r -fo
    mkdir cmake-build

    cmake -B cmake-build -S . "-DCMAKE_TOOLCHAIN_FILE=${Env:VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake"
    cmake --build cmake-build
    cmake-build/Debug/TabugenCpp
}

Generate
RunTest

