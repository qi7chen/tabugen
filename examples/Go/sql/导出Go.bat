echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%
set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taksi\cli.py
set importArgs="user=root,passwd=holyshit,db=test,table=player"
set exportArgs="outdata-dir=%currentDir%,out-src-file=%currentDir%/config.go,pkg=orm"

%taxi_alias%   --mode=mysql --import-args=%importArgs% --generator="go-v2" --export-args=%exportArgs%
go fmt %currentDir%/config.go
pause
REM array-delim