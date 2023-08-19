## 使用Tabugen导出Go


## 示例

### 如何执行

1. 因为使用了泛型相关的API，需要安装[Go SDK 1.21+](https://go.dev/download)
2. 使用powershell执行`Generate.ps1`，即可将excel导出为csv并且生成对应的Go加载解析代码
3. 可选，安装IDE调试环境 [Jetbrains Goland](https://www.jetbrains.com/goland/)


## 生成解析代码

如果指定了生成解析代码，解析函数都被实现在`conv.go`里，在`--with-conv`选项开启的时候，会生成`conv.go`文件。
如果想自己实现`conv.go`里API，用同名文件替换，并在导出的时候不指定`--with-conv`选项。


### meta表里的配置

在excel文件的@meta表里可以定义一些配置来控制如何导入，如：

* `ClassName`  生成的class名称
* `ClassComment`   生成的class注释
* `InnerTypeClass` 嵌入类型的class名称
* `InnerFieldName` 嵌入类型的成员变量名
* `UniqueFields` 对于这些字段，导出的时候会检查每行的数据值是否有重复


### 相关命令行参数

在命令行可以指定一些控制导出内容的参数，如：

* `--go_out` 输出的Go代码文件名
* `--package` 指定Go包名
* `--source_file_encoding` 输出的源代码文件编码格式，默认为UTF-8
* `--with_csv_parse` 是否包含CSV数据加载代码
* `--with-conv` 生成`conv.go`文件
* `--go_fmt` 生成代码文件后，对文件执行go fmt格式化
