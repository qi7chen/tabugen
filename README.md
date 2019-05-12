# taxi

老司机，带你飞

taxi是一个配置导出源码生成工具，旨在简化逻辑开发中的数据抽象过程。


# 为什么要使用taxi配置导出工具


* 可以迅速搭建系统原型

* 支持主流静态语言(C++、C#、Java、Go)

* 对于动态语言，taxi可以导出为json


# taxi的设计

* taxi希望读写配置这件事情应该变得简单快捷；

* taxi希望自身的设计足够简单；


# 如何在开发流程中使用taxi

## 编辑一个excel文件

    一个符合taxi规则的excel表格如下图所示：

![example](doc/img1.png)

    一个excel配置表至少包含2个sheet，默认第一个sheet是数据本身，而另一个指定名称为**meta**的sheet则用来配置导出选项。

    数据定义部分将会导出为结构及相关函数代码定义，而数据本身将会转为另一个csv/json格式的数据文件。

    上图前3行代表这一列的数据类型定义，从第4行开始为数据内容。


## 使用taxi导出excel数据，并生成对应语言的代码
    
    taxi提供了丰富的配置选项来自定义导出需求
    
    
* 导出数据
    将excel导出为csv格式或者json格式的数据

* 导出结构体定义
    导出对应语言的结构定义

* 导出将数据加载到结构的函数
    导出加载数据文件的代码（仅csv格式数据)
    
## 上层业务开发

    前后端拿到各自配置数据及结构定义后，继续进行下一步业务开发

# 各种语言的示例

    请查看examples目录下的taxi导出示例：

* [C++的示例](examples/Cpp) 演示如何配合C++使用;
* [C#的示例](examples/CSharp) 演示如何配合C#(Unity)使用;
* [Golang的示例](examples/Go) 演示如何配合Golang使用;
* [Java的示例](examples/Java) 演示如何配合Java使用;
* 对于python, javascript, lua等动态语言，将excel导出为json即可


# TO-DO

* 提供一个GUI工具；
* 优化excel导出速度；
* 支持csv导出的版本兼容性；
