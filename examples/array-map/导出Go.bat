echo off

set currentDir=%cd%
cd ..\..\
set rootDir=%cd%
cd %currentDir%

set taxi_alias=python %rootDir%\taxi\taxi.py
set importArgs="file=%currentDir%\新手任务.xlsx"
set exportArgs="outdata-dir=%currentDir%,out-src-file=%currentDir%/config.go,pkg=Config"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="go-v1" --export-args=%exportArgs%

pause
REM array-delim