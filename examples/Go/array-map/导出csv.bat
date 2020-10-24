echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%
set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taksi\cli.py
set filepath="%currentDir%\..\..\datasheet\新手任务.xlsx"

%taxi_alias%  --parser=excel --parse_files=%filepath% --go_out=%currentDir%\src\csv\autoconfig.go --with_csv_codegen  --go_fmt --package=config --out_data_format=csv --out_data_path=%currentDir%\res 

pause
REM array-delim