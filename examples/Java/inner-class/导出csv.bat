echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taksi\cli.py
set filepath="%currentDir%\..\..\datasheet\Ëæ»ú±¦Ïä.xlsx"

%taxi_alias%  --parser=excel --parse_files=%filepath% --java_out=%currentDir%\proj\src\main\java --package=com.mycompany.csvconfig --load_code_generator=csv  --out_data_format=csv --out_data_path=%currentDir%\proj\src\main\resources 

pause