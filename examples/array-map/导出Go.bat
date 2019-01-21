echo off

set currentDir=%cd%
cd ..\..\
set rootDir=%cd%
cd %currentDir%

set taxi_alias=python %rootDir%\taxi\taxi.py
set importArgs="file=%currentDir%\新手任务.xlsx"
set exportArgs="pkg=config,outdata-dir=%currentDir%\proj,out-src-file=%currentDir%\proj\autogen.go"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="go-v1" --export-args=%exportArgs%

pause
REM array-delim