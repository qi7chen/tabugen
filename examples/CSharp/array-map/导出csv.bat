echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%
set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taksi\cli.py
set importArgs="file=%currentDir%\新手任务.xlsx"
set exportArgs="pkg=Config,outdata-dir=%currentDir%\res,out-src-file=%currentDir%\src\AutoConfig.cs"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="cs-csv" --output-format=csv --export-args=%exportArgs%

pause
REM array-delim