echo off

set currentDir=%cd%
cd ..\..\
set rootDir=%cd%

set importArgs="file=%currentDir%\新手任务.xlsx"
set exportArgs="outdata-dir=%currentDir%,out-src-file=%currentDir%/config.go,pkg=Config"

python taxi\taxi.py  --mode=excel --import-args=%importArgs% --generator="go-v1" --export-args=%exportArgs%

pause
REM array-delim