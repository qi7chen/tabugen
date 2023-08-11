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
    python $ROOT_DIR/tabugen/__main__.py --asset_path=$excelPath --cpp_out=$outSrcPath --with_csv_parse --package=config --source_file_encoding=utf_8_sig
    python $ROOT_DIR/tabugen/__main__.py --asset_path=$excelPath --out_data_format=csv --out_data_path=$OUT_DATA_DIR
}

Function Generate {
	tabucli 兵种.xlsx SoldierDefine
    tabucli 新手任务.xlsx GuideDefine
    tabucli 随机宝箱.xlsx BoxDefine
    tabucli 全局变量表.xlsx GlobalDefine
}

Function RunTest {
	md cmake-build -ea 0
    cd cmake-build && cmake .. && cmake --build ..
    cmake-build/CppExample
    Set-Location $CURRENT_DIR && rm cmake-build -r -fo
}

# install chocolatey to install cmake
Function Install {
    if (Get-Command choco -errorAction SilentlyContinue) {
        echo 'cmake have installed'
    } else {
        if (Get-Command choco -errorAction SilentlyContinue) {
            echo 'chocolatey have installed'
        } else {
            Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        }
        choco install cmake
    }
}

Install
Generate
RunTest

