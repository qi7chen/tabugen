echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taksi\cli.py
set importArgs="file=%currentDir%\±øÖÖ.xlsx"
set exportArgs="pkg=AutoConfig,encoding=utf-8,outdata-dir=%currentDir%\res,out-src-file=%currentDir%\src\AutoJsonConfig.cs"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="cs-json" --output-format=json --export-args=%exportArgs%

pause