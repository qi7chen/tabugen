<#
# Copyright (C) 2023-present ichenq@outlook.com. All rights reserved.
#>

$CURRENT_DIR = Get-Location
$ROOT_DIR = Resolve-Path "../../"
$DATASHEET_DIR = Resolve-Path "../datasheet"
$OUT_SRC_DIR = Join-Path $CURRENT_DIR  "src"
$OUT_DATA_DIR = Join-Path $DATASHEET_DIR  "/res"

$Env:PYTHONPATH=$ROOT_DIR

Function tabucli {
    $excelPath = Join-Path $DATASHEET_DIR $args[0]
    $outSrcPath = Join-Path $OUT_SRC_DIR $args[1]
    python $ROOT_DIR/tabugen/__main__.py --asset_path=$excelPath --cpp_out=$outSrcPath --with_csv_parse --with_conv --package=config --source_file_encoding=utf_8_sig
    python $ROOT_DIR/tabugen/__main__.py --asset_path=$excelPath --out_data_format=csv --out_data_path=$OUT_DATA_DIR
}

Function Generate {
    tabucli 兵种.xlsx SoldierDefine
    tabucli 新手任务.xlsx GuideDefine
    tabucli 随机宝箱.xlsx BoxDefine
    tabucli 全局变量表.xlsx GlobalDefine
}

# 需要先安装vcpkg，再通过vcpkg安装boost
Function RunTest {
    rm cmake-build -r -fo
    md cmake-build
    cd cmake-build
    
    cmake -B .. -S . "-DCMAKE_TOOLCHAIN_FILE=D:/App/vcpkg/scripts/buildsystems/vcpkg.cmake"
    cmake --build .
    cmake-build/Debug/tabugencpp
}

Generate
RunTest

