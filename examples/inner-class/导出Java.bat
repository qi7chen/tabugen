echo off

set currentDir=%cd%
cd ..\..\
set rootDir=%cd%
cd %currentDir%

set taxi_alias=python %rootDir%\taxi\taxi.py
set importArgs="file=%currentDir%\Ëæ»ú±¦Ïä.xlsx"
set exportArgs="pkg=com.mycompany.config,encoding=gbk,outdata-dir=%currentDir%\proj\csv,out-src-file=%currentDir%\proj"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="java-v1" --export-args=%exportArgs%

pause