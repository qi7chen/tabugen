echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\tabular\cli.py
set filepath="%currentDir%\..\..\datasheet\全局变量表.xlsx"

%taxi_alias% --parse_files=%filepath% --java_out=%currentDir%\idea-project\src\main\java --package=com.mycompany.csvconfig   --with_csv_codegen --out_data_format=csv --out_data_path=%currentDir%\idea-project\src\main\resources 

pause