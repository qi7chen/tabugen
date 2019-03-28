# taxi

老司机，带你飞

taxi是一个配置导出源码生成工具，旨在简化游戏逻辑开发中的数据抽象过程。


# 为什么要使用配置导出工具

* 策划与开发功能规定excel表格格式；

* 双击导出前后端(C++、C#、Java、Go)数据结及配置加载代码；

* 策划开心玩数据，开发专心写业务；


# taxi的设计

* taxi真的希望能带你飞；

* taxi希望读写配置这件事情应该变得简单，但不追求大而全；

* taxi使用python3编写，并提供执行档发布；



# 如何使用taxi导出数据

一个符合taxi规则的excel表格如下图所示：
![example](doc/img1.png)

按taxi的规则，一个excel配置表包含了两大内容，一个是对数据的定义，包括每一列的名称、类型等，还有一些配合导出的选项，二个是数据本身。

数据定义部分将会导出为结构及相关函数代码定义，而数据本身将会转为另一个csv格式的文件。

上图前3行代表这一列的数据类型定义，从第4行开始为数据内容。

另外，每一个excel表格都必须带有一个名为**meta**的sheet，在这个sheet里定义相关的程序导出参数。

请查看examples目录下的示例：

* [示例1](examples/C#/basic) 演示excel配置的基础用法，导出为C#(Unity);
* [示例2](examples/C++/global-var) 演示如何配置全局参数表，导出为C++;
* [示例3](examples/Go/array-map) 演示如何使用array和map类型，导出为Go;
* [示例4](examples/Java/inner-class) 演示如何在excel内部再定义嵌入类型，导出为Java;
* [示例5](examples/Go/sql) 演示如何从MySQL数据库导出代码，导出为Go;


# TO-DO

* 支持导出为JSON和Lua；
* 优化excel导出速度；
* 支持csv导出的版本兼容性；
