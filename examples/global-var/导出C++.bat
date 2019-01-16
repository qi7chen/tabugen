echo off

set currentDir=%cd%
cd ..\..\
set rootDir=%cd%
cd %currentDir%

set taxi_alias=python %rootDir%\taxi\taxi.py
set importArgs="file=%currentDir%\全局变量表.xlsx"
set exportArgs="outdata-dir=%currentDir%,out-src-file=%currentDir%/AutoGenConfig,pkg=config"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="cpp-v1" --export-args=%exportArgs%

pause