echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\tabular\cli.py
set filepath="%currentDir%\..\..\datasheet\全局变量表.xlsx"

%taxi_alias%  --parse_files=%filepath% --go_out=%currentDir%\src\csv\autoconfig.go --gen_csv_parse  --go_fmt --package=config --out_data_format=csv --out_data_path=%currentDir%\res 

pause