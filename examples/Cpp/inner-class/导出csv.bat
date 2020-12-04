echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\tabular\cli.py
set filepath="%currentDir%\..\..\datasheet\Ëæ»ú±¦Ïä.xlsx"

%taxi_alias% --parse_files=%filepath% --cpp_out=%currentDir%\src\AutogenConfig --with_csv_codegen   --source_file_encoding=gbk --out_data_format=csv --out_data_path=%currentDir%\res 

pause