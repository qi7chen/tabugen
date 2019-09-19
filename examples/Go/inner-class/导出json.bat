echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taksi\cli.py
set importArgs="file=%currentDir%\Ëæ»ú±¦Ïä.xlsx"
set exportArgs="pkg=config, outdata-dir=%currentDir%\res,out-src-file=%currentDir%\src\json\autoconfig.go"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="go-json" --output-format=json --export-args=%exportArgs%

pause