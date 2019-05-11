echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taxi\cli.py
set importArgs="file=%currentDir%\res\全局变量表.xlsx"
set exportArgs="pkg=config, outdata-dir=%currentDir%\res,out-src-file=%currentDir%\src\autoconfig.go"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="go-json" --output-format=json --export-args=%exportArgs%

pause