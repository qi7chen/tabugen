## 使用Tabugen导出Go


## 示例

### 如何执行

1. 因为使用了泛型相关的API，需要安装[Go SDK 1.21+](https://go.dev/download)
2. 使用powershell执行`Generate.ps1`，即可将excel导出为csv并且生成对应的Go加载解析代码
3. 可选，安装IDE调试环境 [Jetbrains Goland](https://www.jetbrains.com/goland/)


## 解析代码

* `table.go`源码文件包含了常用的从字符串解析基本类型的实现以及csv文件的读取；
* `all_test.go` 是单元测试代码，用于测试解析代码的正确性；


### 相关命令行参数

在命令行可以指定一些控制导出内容的参数，如：

* `--go_out` 输出的Go代码文件名
* `--package` 指定Go包名
* `--gen_csv_parse` 是否生成代码中包含CSV数据加载函数，一般命名为`ParseRow()`
* `--go_fmt` 生成代码文件后，对文件执行go fmt格式化
* `--source_file_encoding` 输出的源代码文件编码格式，默认为UTF-8
* `--file_asset` 指定输入的Excel文件或者目录
* `--file_skip` 指定不导出的Excel文件
* `--without_data` 不导出数据，只导出Go代码
* `--project_kind` 指定解析特定的字段类型，如`--project_kind=C`，只解析`C_`开头和不带kind的字段
* `--delim1` 指定第一级分隔符，默认为`|`
* `--delim2` 指定第二级分隔符，默认为`:`
* `--data_file_encoding` 输出的数据文件编码格式，默认为UTF-8
* `--out_data_format` 数据文件输出格式，默认为`csv`，可以选择`json`
* `--out_data_path` 输出的数据文件路径，默认为当前目录
* `--json_indent` 输出的json文件使用缩进格式
* `--json_snake_case` 输出的json文件使用蛇形命名格式

