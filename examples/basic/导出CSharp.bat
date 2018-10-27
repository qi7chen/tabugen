echo off

set currentDir=%cd%
cd ..\..\
set rootDir=%cd%

set importArgs="file=%currentDir%\±øÖÖ.xlsx"
set exportArgs="outdata-dir=%currentDir%,out-src-file=%currentDir%/Config.cs,pkg=Config"

python taxi\taxi.py  --mode=excel --import-args=%importArgs% --generator="cs-v1" --export-args=%exportArgs%

pause