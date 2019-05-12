echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taxi\cli.py
set importArgs="file=%currentDir%\新手任务.xlsx"
set exportArgs="pkg=com.mycompany.csvconfig,outdata-dir=%currentDir%\proj\src\main\resources,out-src-file=%currentDir%\proj\src\main\java"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="java-csv" --output-format=csv --export-args=%exportArgs%

pause