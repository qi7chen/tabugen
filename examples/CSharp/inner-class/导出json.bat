echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taxi\cli.py
set importArgs="file=%currentDir%\Ëæ»ú±¦Ïä.xlsx"
set exportArgs="pkg=AutoConfig, outdata-dir=%currentDir%\res,out-src-file=%currentDir%\src\AutoJsonConfig.cs"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="cs-json" --output-format=json --export-args=%exportArgs%

pause