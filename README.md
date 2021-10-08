Tabugen
====

Tabugen是一个配置导出和代码生成工具。

Tabugen导入Excel表格生成编程语言的结构体定义，导出CSV数据文件，并生成对应的CSV文件加载代码，旨在简化业务开发中的数据抽象过程。


# Tabugen特性(Features)
====

* 支持主流静态语言(C++、C#、Java、Go)的代码生成
* 支持配置简单数组和字典类型
* 自动生成CSV数据加载代码


# 如何使用Tabugen(How to Use)
====

How to Use

编辑一个excel文件
====

将excel表格的数据sheet按第1行为字段名称、第2行为数据类型、第3行为注释，从第4行开始为数据内容的格式编辑

导出数据和生成代码
====

运行Tabugen脚本，生成C#代码和导出CSV数据文件

`pip install tabugen`

`python tabugen/cli.py --parse_files=example.xlsx --csharp_out=AutoConfig.cs --package=Config`



各种语言的示例
====

请查看examples目录下的tabugen导出示例：

* C++的示例 examples/Cpp 演示如何配合C++使用;
* C#的示例 examples/CSharp 演示如何配合C#(Unity)使用;
* Golang的示例 examples/Go 演示如何配合Golang使用;
* Java的示例 examples/Java 演示如何配合Java使用;
* 对于python, javascript, lua等动态语言，将excel导出为json即可

TO-DO
====

* 部分细节优化；
