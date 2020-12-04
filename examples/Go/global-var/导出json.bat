echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\tabular\cli.py
set filepath="%currentDir%\..\..\datasheet\全局变量表.xlsx"

%taxi_alias%  --parse_files=%filepath% --enable_column_skip --go_out=%currentDir%\src\json\autoconfig.go --go_json_tag  --go_fmt --package=config --out_data_format=json --json_indent --json_snake_case  --out_data_path=%currentDir%\res 

pause