echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%
set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taksi\cli.py
set filepath="%currentDir%\..\..\datasheet\新手任务.xlsx"

%taxi_alias%  --parser=excel --parse_files=%filepath% --csharp_out=%currentDir%\src\AutoJsonConfig.go --package=Config2 --out_data_format=json --json_indent  --out_data_path=%currentDir%\res 

pause
REM array-delim