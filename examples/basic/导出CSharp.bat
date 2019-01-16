echo off

set currentDir=%cd%
cd ..\..\
set rootDir=%cd%
cd %currentDir%

set taxi_alias=python %rootDir%\taxi\taxi.py
set importArgs="file=%currentDir%\±øÖÖ.xlsx"
set exportArgs="outdata-dir=%currentDir%,out-src-file=%currentDir%/Config.cs,pkg=Config"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="cs-v1" --export-args=%exportArgs%

pause