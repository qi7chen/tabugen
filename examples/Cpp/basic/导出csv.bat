echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taxi\cli.py
set importArgs="file=%currentDir%\±øÖÖ.xlsx"
set exportArgs="pkg=autogen,src-encoding=gbk,data-encoding=gbk,outdata-dir=%currentDir%\res,out-src-file=%currentDir%\src\AutogenConfig"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="cpp-csv" --output-format=csv  --export-args=%exportArgs%

pause