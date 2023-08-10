<#
# Copyright (C) 2023-present ichenq@outlook.com. All rights reserved.
#>

$CURRENT_DIR = Get-Location
$ROOT_DIR = Resolve-Path "../../"
$DATASHEET_DIR = Resolve-Path "../datasheet"
$OUT_SRC_DIR = Join-Path $CURRENT_DIR  "src/main/java"
$OUT_DATA_DIR = Join-Path $DATASHEET_DIR  "/res"


$Env:PYTHONPATH=$ROOT_DIR

Function tabucli {
    $excelPath = Join-Path $DATASHEET_DIR $args[0]
    python $ROOT_DIR/tabugen/__main__.py --asset_path=$excelPath --java_out=$OUT_SRC_DIR --with_csv_parse --package=com.pdfun.config
    python $ROOT_DIR/tabugen/__main__.py --asset_path=$excelPath --out_data_format=csv --out_data_path=$OUT_DATA_DIR
    python $ROOT_DIR/tabugen/__main__.py --asset_path=$excelPath --out_data_format=json --json_indent --out_data_path=$OUT_DATA_DIR
}

Function Generate {
	tabucli 兵种.xlsx
    tabucli 新手任务.xlsx
    tabucli 随机宝箱.xlsx
    tabucli 全局变量表.xlsx
}

Function RunTest {
    mvn compile
    mvn exec:java -Dexec.mainClass="Sample"
    mvn clean
}

# install chocolatey to install cmake
Function Install {
    if (Get-Command mvn -errorAction SilentlyContinue) {
        echo 'maven have installed'
    } else {
        if (Get-Command choco -errorAction SilentlyContinue) {
            echo 'chocolatey have installed'
        } else {
            Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        }
        choco install maven
    }
}

Install
Generate
RunTest

