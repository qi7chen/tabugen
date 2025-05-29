## 各种语言的示例


* [C++的示例](Cpp) 演示如何配合C++使用;
* [C#的示例](CSharp) 演示如何配合C#(Unity)使用;
* [Golang的示例](Go) 演示如何配合Golang使用;


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


#### meta表的配置参数

在excel文件的@meta表里可以定义一些配置来控制如何导入，如：

* `class_name`  生成的class名称
* `class_comment`   生成的class注释
* `parse_kv_mode` 是否为全局变量表模式
* `inner_type_class` 嵌入类型的class名称
* `inner_type_name` 嵌入类型的成员变量名
* `unique_columns` 对于这些列，导出的时候会检查每行的数据值是否有重复
