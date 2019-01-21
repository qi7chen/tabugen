## array和map类型演示

双击`导出Go.bat`文件即可导出Go代码

需要依赖 openpyxl, pymysql

`pip install openpyxl pymysql`


taxi支持将一列数据的类型配置为数组或者是键值对格式，也就是对应的array和map，配置格式参考C++语法，使用array<int>或者map<string,int>即可。
如下图所示：
![example](../../doc/img3.png)


## 配置详解


### meta表里的配置

在excel文件的meta表里可以定义一些配置来控制如何导入，如：

* `class-name`  生成的class名称	
* `class-comment`   生成的class注释
* `type-row` 定义每个字段类型的行，不填写则默认为第1行
* `name-row` 每个字段的名称所在行，不填写则默认为第2行
* `comment-row` 每个字段的注释行，不填写则默认为第3行
* `data-start-row` 数据从哪一行开始，不填写则默认为第4行
* `data-end-row` 数据从哪一行结束，不填写则默认为为最后一行
* `get-keys` 配置生成Get函数包含的参数（列），以逗号分隔，Get函数返回一个最匹配参数的配置项；
* `range-keys`  配置生成GetRange函数包含的参数（列），以逗号分隔，GetRange函数返回一组匹配参数的配置项；
* `hide-value-column` 对于这些列，它们的值会在hide-column选项开启的时候置空
* `inner-type-range`  解析为嵌入类型的字段范围，用例见[示例4](../inner-class)
* `inner-type-class` 嵌入类型的class名称，用例见[示例4](../inner-class)
* `inner-type-name` 嵌入类型的成员变量名，用例见[示例4](../inner-class)

### import-args参数

在命令行可以指定一些控制导出内容的参数，如：

* `outdata-dir` 导出csv的存放路径
* `outdata-src-file` 导出源文件的路径及名称
* `pkg` 生成的命名空间
* `pch` C++的预编译头名称
* `auto-vector` 自动把相同的列合并为数据，例如有attr1, attr2, attr3这三列，会被合并为attr[3]
* `data-only` 只导出csv数据，不导出源码文件；
* `no-data` 只导出源码文件，不导出数据；
* `hide-column` 导出时置空由`hide-value-column`
* `encoding` 导出文件(包括源码和csv)的编码格式，默认为utf-8
* `array-delim` 数组字段的分隔符，默认为`|`， 如 `A|B|C`
* `map-delim` 字典字段的2个分隔符，默认为`|=`，如 `A=x|B=y|A=z` 