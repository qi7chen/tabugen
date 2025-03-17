<#
# Copyright (C) 2023-present qi7chen@github. All rights reserved.
#>

$CURRENT_DIR = Get-Location
$ROOT_DIR = Resolve-Path "../../"
$DATASHEET_DIR = Resolve-Path "../datasheet"
$OUT_SRC_DIR = Join-Path $CURRENT_DIR  "src"
$OUT_DATA_DIR = Join-Path $DATASHEET_DIR  "res"

$Env:PYTHONPATH=$ROOT_DIR

Function Generate {
    python $ROOT_DIR/tabugen/__main__.py --file_asset=$DATASHEET_DIR --go_out=$OUT_SRC_DIR/config.go --package=config --gen_csv_parse --go_fmt --out_data_path=$OUT_DATA_DIR --out_data_format=csv
    python $ROOT_DIR/tabugen/__main__.py --file_asset=$DATASHEET_DIR --out_data_path=$OUT_DATA_DIR  --out_data_format=json --json_indent
}

Function RunTest {
    $Env:GO111MODULE='off'
    Set-Location $OUT_SRC_DIR
    go test -v
    Set-Location $CURRENT_DIR
}

Generate
RunTest

