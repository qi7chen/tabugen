## 使用Tabugen导出Java


## 示例说明

1. 需要安装[maven](https://maven.apache.org/)
2. 使用powershell执行`Generate.ps1`，即可将excel导出为csv并且生成对应的Java加载解析代码



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


