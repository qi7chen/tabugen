echo off

set currentDir=%cd%
cd ..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taxi\cli.py
set importArgs="file=%currentDir%\全局变量表.xlsx"
set exportArgs="pkg=config, encoding=gbk, outdata-dir=%currentDir%\proj,out-src-file=%currentDir%\proj\AutoGenConfig"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="cpp-v1" --export-args=%exportArgs%

pause