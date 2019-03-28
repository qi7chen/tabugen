echo off

set currentDir=%cd%
cd ..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taxi\cli.py
set importArgs="file=%currentDir%\±øÖÖ.xlsx"
set exportArgs="pkg=Config,encoding=utf-8,outdata-dir=%currentDir%\proj,out-src-file=%currentDir%\proj\AutoConfig.cs"

%taxi_alias%  --mode=excel --import-args=%importArgs% --generator="cs-v1" --export-args=%exportArgs%

pause