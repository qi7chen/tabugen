echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\tabular\cli.py
set filepath="%currentDir%\..\..\datasheet\Ëæ»ú±¦Ïä.xlsx"

%taxi_alias% --parse_files=%filepath%  --csharp_out=%currentDir%\src\AutoConfig.cs --package=Config --with_csv_codegen   --out_data_format=csv --out_data_path=%currentDir%\res 

pause