echo off

set currentDir=%cd%
cd ..\..\
set rootDir=%cd%
cd %currentDir%

set taxi_alias=python %rootDir%\taxi\taxi.py
set importArgs="file=%currentDir%\Ëæ»ú±¦Ïä.xlsx"
set exportArgs="outdata-dir=%currentDir%,out-src-file=%currentDir%,pkg=com.mycompany.config"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="java-v1" --export-args=%exportArgs%

pause