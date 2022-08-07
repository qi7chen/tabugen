## 使用Tabugen导出Java


## 示例说明

需要安装[maven](https://maven.apache.org/)

* 执行`make generate`，即可导出默认选项的Java代码
* 执行`make output`导出csv和json
* 执行`make run`运行测试用例


## 配置详解

### meta表里的配置

在excel文件的@meta表里可以定义一些配置来控制如何导入，如：

* `ClassName`  生成的class名称
* `ClassComment`   生成的class注释
* `InnerTypeClass` 嵌入类型的class名称
* `InnerFieldName` 嵌入类型的成员变量名
* `UniqueFields` 对于这些字段，导出的时候会检查每行的数据值是否有重复

### 相关命令行参数

在命令行可以指定一些控制导出内容的参数，如：

* `--java_out` 输出的Java代码包路径
* `--package` 指定Java包名
* `--source_file_encoding` 输出的源代码文件编码格式，默认为UTF-8
* `--with_csv_parse` 是否包含CSV数据加载代码


