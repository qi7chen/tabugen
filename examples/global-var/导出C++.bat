echo off

set currentDir=%cd%
cd ..\..\
set rootDir=%cd%

set importArgs="file=%currentDir%\全局变量表.xlsx"
set exportArgs="outdata-dir=%currentDir%,out-src-file=%currentDir%/AutoGenConfig,pkg=config"

python taxi\taxi.py  --mode=excel --import-args=%importArgs% --generator="cpp-v1" --export-args=%exportArgs%

pause