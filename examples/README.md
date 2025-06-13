## 各种语言的示例


* [C++的示例](Cpp) 演示如何配合C++使用;
* [C#的示例](CSharp) 演示如何配合C#(Unity)使用;
* [Golang的示例](Go) 演示如何配合Golang使用;


## 其它动态语言

  Tabugen支持将excel导出为json，对于python, javascript, lua等动态语言，可直接加载json文件拿到结构定义。

## 基本使用

#### 命令行参数

* `--file_asset` 指定导入的excel文件，或者包含很多excel文件的路径名称
* `--file_skip` 需要跳过的excel文件名
* `--out_data_format` 导出的数据文件格式，可以是csv，json
* `--out_data_path` 导出的数据文件路径
* `--delim1` 导出代码里使用的列表元素分隔符
* `--delim2` 导出代码里使用的键值元素分隔符
* `--data_file_encoding` 导出数据文件的编码格式，默认UTF-8
* `--json_indent` 控制导出的JSON是否换行
* `--json_snake_case` 控制导出的JSON使用字段名称是小写还是大写驼峰风格
