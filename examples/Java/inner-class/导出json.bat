echo off

set currentDir=%cd%
cd ..\..\..\
set rootDir=%cd%
cd %currentDir%

set PYTHONPATH=%rootDir%

set taxi_alias=python %rootDir%\taksi\cli.py
set filepath="%currentDir%\..\..\datasheet\Ëæ»ú±¦Ïä.xlsx"

%taxi_alias%  --parser=excel --parse_files=%filepath% --java_out=%currentDir%\idea-project\src\main\java --package=com.mycompany.jsonconfig --out_data_format=json --json_indent  --out_data_path=%currentDir%\idea-project\src\main\resources

pause