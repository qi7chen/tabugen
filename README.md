# TAKSi

老司机，带你飞

TAKSi是一个从配置(excel表格）生成对应语言源码的工具，旨在简化游戏业务开发中的数据抽象过程。


# TAKSi特性

* 支持主流静态语言(C++、C#、Java、Go)的代码生成

* 支持配置简单数组和字典类型

* 自动生成CSV数据加载代码


# 如何使用TAKSi

## 编辑一个excel文件

    一个符合TAKSi规则的excel表格如下图所示：

![example](doc/img1.png)

    一个excel配置表至少包含2个sheet，默认第一个sheet是数据本身，而另一个指定名称为**@meta**的sheet则用来配置导出选项。

    数据定义部分将会导出为结构及相关函数代码定义，而数据本身将会转为另一个csv/json格式的数据文件。

    上图前3行代表这一列的数据类型定义，第1行为字段名称，第2行为数据类型，第3行为注释，从第4行开始为数据内容。


# 各种语言的示例

    请查看examples目录下的TAKSi导出示例：

* [C++的示例](examples/Cpp) 演示如何配合C++使用;
* [C#的示例](examples/CSharp) 演示如何配合C#(Unity)使用;
* [Golang的示例](examples/Go) 演示如何配合Golang使用;
* [Java的示例](examples/Java) 演示如何配合Java使用;
* 对于python, javascript, lua等动态语言，将excel导出为json即可


# 如何打包TAKSi成执行档

Windows上没有默认安装Python环境，可以使用PyInstaller将TAKSi打包成执行档发布

`
pip install -r requirements.txt

pyinstaller -F --name=taksi taksi\cli.py
`

# TO-DO

* 优化excel导出速度；
* 提供[WebGUI](https://adminlte.io/preview)后台，实现配置数据查看、编辑，方便非技术人员进行数值更改、验证；
