## 使用Tabugen导出Go


## 示例

* 执行`make generate`，即可生成默认的Go代码
* 执行`make output`导出csv和json
* 执行`make run`运行默认测试用例


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

* `--go_out` 输出的Go代码文件名
* `--package` 指定Go包名
* `--source_file_encoding` 输出的源代码文件编码格式，默认为UTF-8
* `--config_manager_class` 指定管理配置的class名称，默认为AutogenConfigManager
* `--with_csv_parse` 是否包含CSV数据加载代码
* `--go_fmt` 生成代码文件后，对文件执行go fmt格式化
