echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%
set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taksi\cli.py
set filepath="%currentDir%\..\..\datasheet\新手任务.xlsx"

%taxi_alias%  --parser=excel --parse_files=%filepath% --cpp_out=%currentDir%\src\AutogenConfig --load_code_generator=csv  --source_file_encoding=gbk --out_data_format=csv --out_data_path=%currentDir%\res 

pause
