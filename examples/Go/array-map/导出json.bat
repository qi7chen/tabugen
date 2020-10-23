echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%
set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taksi\cli.py
set filepath=%currentDir%\新手任务.xlsx

%taxi_alias%  --parser=excel --parse_files=%filepath% --go_out=%currentDir%\src\json\autoconfig.go --load_code_generator=json --go_fmt --package=config --out_data_format=csv --out_data_path=%currentDir%\res 

pause
REM array-delim