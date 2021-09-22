## 使用Tabugen导出C#


## 示例说明

* [basic](basic) 演示基本使用
    在excel里默认第1栏为字段名称，第2栏为数据类型，第3栏为注释文字，数据内容从第4栏开始。
    
* [array-map](array-map) 演示如何配置数组和字典类型
    Tabugen支持在excel配置简单的数组和字典类型（不支持嵌套），并会生成对数组和字典类型的读取代码（仅csv格式)。
    
* [global-var](global-var) 演示全局变量表的使用
    Tabugen支持全局参数表配置，这是一种全局的key-value配置，在形式上是纵向配置。
    
* [inner-class](inner-class) 演示如何合并多组列为嵌套类
    当一个表里有很多重复的连续字段的时候，可以把它们导出为一个嵌入类型，
    比如`name1, id1, name2, id2, name3, id3`, 可以将其导出为一个包含`name, id`字段的嵌套类型。
    
    
执行`make run`，即可导出默认选项的C#代码及CSV和JSON数据文件


## 配置详解


### meta表里的配置

在excel文件的@meta表里可以定义一些配置来控制如何导入，如：

* `class_name`  生成的class名称	
* `class_comment`   生成的class注释
* `name_row` 指定字段名称所在行，默认为第1行
* `type_row` 指定字段类型所在行，默认为第2行
* `comment_row` 指定字段名称所在行，默认为第3行
* `data_start_row` 数据从哪一行开始，默认为第4行
* `data_end_row` 数据在哪一行结束，默认为为最后一行
* `parse_kv_mode` 是否为全局变量表模式
* `key_value_column` KV模式中的key和value所在列
* `value_type_column` KV模式中的value类型所在列
* `inner_type_range`  解析为嵌入类型的字段范围
* `inner_type_class` 嵌入类型的class名称
* `inner_type_name` 嵌入类型的成员变量名
* `get_keys` 配置生成Get函数包含的参数（列），以逗号分隔，Get函数返回一个最匹配参数的配置项；
* `range_keys`  配置生成GetRange函数包含的参数（列），以逗号分隔，GetRange函数返回一组匹配参数的配置项；
* `hide_value_columns` 对于这些列，它们的值会在hide-column选项开启的时候置空
* `unique_columns` 对于这些列，导出的时候会检查每行的数据值是否有重复

### 相关命令行参数

在命令行可以指定一些控制导出内容的参数，如：

* `--csharp_out` 输入为C#代码文件
* `--package` 指定C#命名空间
* `--source_file_encoding` 输出的源代码文件编码格式，默认为UTF-8
* `--config_manager_class` 指定管理配置的class名称，默认为AutogenConfigManager
* `--gen_csv_parse` 是否包含CSV解析代码
* `--gen_csv_dataload` 是否包含CSV数据加载代码

