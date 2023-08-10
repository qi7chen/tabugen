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
    python $ROOT_DIR/tabugen/__main__.py --asset_path=$excelPath --cs_out=$outSrcPath --with_csv_parse --package=Config --json_snake_case
    python $ROOT_DIR/tabugen/__main__.py --asset_path=$excelPath --out_data_format=csv --out_data_path=$OUT_DATA_DIR
    python $ROOT_DIR/tabugen/__main__.py --asset_path=$excelPath --out_data_format=json --json_indent --out_data_path=$OUT_DATA_DIR
}

Function Generate {
	tabucli 兵种.xlsx SoldierDefine.cs
    tabucli 新手任务.xlsx GuideDefine.cs
    tabucli 随机宝箱.xlsx GlobalDefine.cs
    tabucli 全局变量表.xlsx BoxDefine.cs
}

Function RunTest {
    cd src
    dotnet run
}

# install chocolatey to install .net core
Function Install {
    if (Get-Command dotnet -errorAction SilentlyContinue) {
        echo 'dotnetcore have installed'
    } else {
        if (Get-Command choco -errorAction SilentlyContinue) {
            echo 'chocolatey have installed'
        } else {
            Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        }
        choco install choco install dotnetcore-sdk
    }
}

Install
Generate
RunTest

