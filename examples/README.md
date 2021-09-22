## 各种语言的示例


* [C++的示例](Cpp) 演示如何配合C++使用;
* [C#的示例](CSharp) 演示如何配合C#(Unity)使用;
* [Golang的示例](Go) 演示如何配合Golang使用;
* [Java的示例](Java) 演示如何配合Java使用;

## 其它动态语言
 
    Tabugen支持将excel导出为json，对于python, javascript, lua等动态语言，可直接加载json文件拿到结构定义。
    
## 基本使用

#### 命令行参数

* `--parse_files` 指定导入的excel文件，或者包含很多excel文件的路径名称
* `--parse_file_skip` 需要跳过的excel文件名
* `--enable_column_skip` 如果开启这个选项，则excel里配置hide_value_columns包含的列不会被导入
* `--out_data_format` 导出的数据文件格式，可以是csv，json
* `--out_data_path` 导出的数据文件路径
* `--data_file_encoding` 导出数据文件的编码格式，默认UTF-8
* `--out_csv_delim` 导出的CSV数据文件的分隔符，默认为逗号
* `--json_indent` 控制导出的JSON是否换行
* `--json_snake_case` 控制导出的JSON使用字段名称是小写还是大写驼峰风格
* `--array_delim`指定表格数据里的array类型的分隔符，默认是逗号，即数据配置格式为 "1,2,3"
* `--map_delims` 指定表格数据里的map类型的分隔符，默认是分号和等号，即数据配置格式为 "a=1;b=2;c=3"

#### meta表的配置参数

在excel文件的@meta表里可以定义一些配置来控制如何导入，如：

* `class_name`  生成的class名称	
* `class_comment`   生成的class注释
* `name_row` 指定字段名称所在行，默认为第1行
* `type_row` 指定字段类型所在行，默认为第2行
* `comment_row` 指定字段名称所在行，默认为第3行
* `data_start_row` 数据从哪一行开始，默认为第4行
* `data_end_row` 数据在哪一行结束，默认为为最后一行
* `parse_kv_mode` 是否为全局变量表模式
* `key_value_column` KV模式中的key和value所在列
* `value_type_column` KV模式中的value类型所在列
* `inner_type_range`  解析为嵌入类型的字段范围
* `inner_type_class` 嵌入类型的class名称
* `inner_type_name` 嵌入类型的成员变量名
* `get_keys` 配置生成Get函数包含的参数（列），以逗号分隔，Get函数返回一个最匹配参数的配置项；
* `range_keys`  配置生成GetRange函数包含的参数（列），以逗号分隔，GetRange函数返回一组匹配参数的配置项；
* `hide_value_columns` 对于这些列，它们的值会在hide-column选项开启的时候置空
* `unique_columns` 对于这些列，导出的时候会检查每行的数据值是否有重复
