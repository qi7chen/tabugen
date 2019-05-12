## 使用taxi导出C#


## 示例说明

* [basic](example/CSharp/basic) 演示基本使用
    在excel里默认第1栏为数据类型，第2栏为字段名称，第3栏为注释文字，数据内容从第4栏开始。
    
* [array-map](example/CSharp/array-map) 演示如何配置数组和字典类型
    taxi支持在excel配置简单的数组和字典类型（不支持嵌套），并会生成对数组和字典类型的读取代码（仅csv格式)。
    
* [global-var](example/CSharp/global-var) 演示全局变量表的使用
    taxi支持全局参数表配置，这是一种全局的key-value配置，在形式上是纵向配置。
    
* [inner-class](example/CSharp/inner-class) 演示如何合并多组列为嵌套类
    当一个表里有很多重复的连续字段的时候，可以把它们导出为一个嵌入类型，
    比如`name1, id1, name2, id2, name3, id3`, 可以将其导出为一个包含`name, id`字段的嵌套类型。
    
    
双击`导出csv.bat`，即可导出默认选项的C#代码及csv数据文件

双击`导出json.bat`，即可导出默认选项的C#代码及json数据文件


## 配置详解


### meta表里的配置

在excel文件的meta表里可以定义一些配置来控制如何导入，如：

* `class-name`  生成的class名称	
* `class-comment`   生成的class注释
* `type-row` 指定字段类型所在行，默认为第1行
* `name-row` 指定字段名称所在行，默认为第2行
* `comment-row` 指定字段名称所在行，默认为第3行
* `data-start-row` 数据从哪一行开始，默认为第4行
* `data-end-row` 数据在哪一行结束，默认为为最后一行
* `get-keys` 配置生成Get函数包含的参数（列），以逗号分隔，Get函数返回一个最匹配参数的配置项；
* `range-keys`  配置生成GetRange函数包含的参数（列），以逗号分隔，GetRange函数返回一组匹配参数的配置项；
* `hide-value-column` 对于这些列，它们的值会在hide-column选项开启的时候置空
* `inner-type-range`  解析为嵌入类型的字段范围，用例见[示例4](../inner-class)
* `inner-type-class` 嵌入类型的class名称，用例见[示例4](../inner-class)
* `inner-type-name` 嵌入类型的成员变量名，用例见[示例4](../inner-class)

### import-args参数

在命令行可以指定一些控制导出内容的参数，如：

* `outdata-dir` 导出csv在哪个路径下
* `out-src-file` 导出源文件和头文件的名称（不包含后缀名）
* `pkg` 定义C++命名空间
* `pch` 指定包含的C++的预编译头名称
* `auto-vector` 自动把相同的列合并为数据，例如有attr1, attr2, attr3这三列，会被合并为attr[3]
* `hide-column` 导出时置空由`hide-value-column`
* `src-encoding` 导出源码文件的编码格式，默认为utf-8
* `data-encoding` 导出数据文件的编码格式，默认为utf-8
* `array-delim` 数组字段的分隔符，默认为`|`， 如 `A|B|C`
* `map-delim` 字典字段的2个分隔符，默认为`|=`，如 `A=x|B=y|A=z` 
