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
    python $ROOT_DIR/tabugen/__main__.py --asset_path=$excelPath --go_out=$outSrcPath --with_csv_parse --package=config --go_fmt
    python $ROOT_DIR/tabugen/__main__.py --asset_path=$excelPath --out_data_format=csv --out_data_path=$OUT_DATA_DIR
    python $ROOT_DIR/tabugen/__main__.py --asset_path=$excelPath --out_data_format=json --json_indent --out_data_path=$OUT_DATA_DIR
}

Function Generate {
    tabucli 兵种.xlsx soldier_define.go
    tabucli 新手任务.xlsx guide_define.go
    tabucli 随机宝箱.xlsx box_define.go
    tabucli 全局变量表.xlsx global_define.go
}

Function RunTest {
    $Env:GO111MODULE='off'
    Set-Location $OUT_SRC_DIR
    go test -v
    Set-Location $CURRENT_DIR
}

Generate
RunTest

