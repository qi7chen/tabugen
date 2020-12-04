
currentDir=`pwd`
cd ../../../
rootDir=`pwd`
cd $currentDir

export PYTHONPATH=$rootDir
alias taxi_alias='python $rootDir/tabular/cli.py'
filepath=$currentDir/../../datasheet/兵种.xlsx
taxi_alias --parse_files=$filepath --enable_column_skip --cpp_out=$currentDir/src/AutogenConfig --with_csv_codegen --out_data_format=csv --out_data_path=$currentDir/res 

