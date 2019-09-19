echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taksi\cli.py
set importArgs="file=%currentDir%\Ëæ»ú±¦Ïä.xlsx"
set exportArgs="pkg=config,src-encoding=gbk,outdata-dir=%currentDir%\res,out-src-file=%currentDir%\src\AutogenConfig"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="cpp-csv" --output-format=csv --export-args=%exportArgs%

pause