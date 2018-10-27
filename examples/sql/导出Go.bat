echo off

set currentDir=%cd%
cd ..\..\
set rootDir=%cd%

set importArgs="user=root,passwd=holyshit,db=test,table=player"
set exportArgs="outdata-dir=%currentDir%,out-src-file=%currentDir%/config.go,pkg=orm"

python taxi\taxi.py  --mode=mysql --import-args=%importArgs% --generator="go-v2" --export-args=%exportArgs%

pause
REM array-delim