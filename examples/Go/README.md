## 使用Tabugen导出Go


## 示例

### 目录说明

* [basic](basic) 演示基本使用
    在excel里默认第1栏为字段名称，第2栏为数据类型，第3栏为注释文字，数据内容从第4栏开始。

* [array-map](array-map) 演示如何配置数组和字典类型
    Tabugen支持在excel配置简单的数组和字典类型（不支持嵌套），并会生成对数组和字典类型的读取代码（仅csv格式)。

* [global-var](global-var) 演示全局变量表的使用
    Tabugen支持全局参数表配置，这是一种全局的key-value配置，在形式上是纵向配置。

* [inner-class](inner-class) 演示如何合并多组列为嵌套类
    当一个表里有很多重复的连续字段的时候，可以把它们导出为一个嵌入类型，
    比如`name1, id1, name2, id2, name3, id3`, 可以将其导出为一个包含`name, id`字段的嵌套类型。


### 使用make

* 执行`make run`，即可导出默认选项的Go代码及csv、json数据文件


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
* `--go_json_tag` 生成Go字段的json tag
* `--go_fmt` 生成代码文件后，对文件执行go fmt格式化
