echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taxi\cli.py
set importArgs="file=%currentDir%\res\Ëæ»ú±¦Ïä.xlsx"
set exportArgs="pkg=config, outdata-dir=%currentDir%\res,out-src-file=%currentDir%\src\csv\autoconfig.go"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="go-csv" --output-format=csv --export-args=%exportArgs%

pause