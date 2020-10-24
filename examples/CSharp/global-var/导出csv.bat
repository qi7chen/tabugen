echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taksi\cli.py
set filepath="%currentDir%\..\..\datasheet\全局变量表.xlsx"

%taxi_alias%  --parser=excel --parse_files=%filepath%  --csharp_out=%currentDir%\src\AutoConfig.cs --package=Config --with_csv_codegen   --out_data_format=csv --out_data_path=%currentDir%\res 

pause