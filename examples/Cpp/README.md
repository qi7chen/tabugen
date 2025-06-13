## 使用Tabugen导出C++


## 示例

### 如何编译

1. 需要安装[Visual C++](https://www.visualstudio.com)和 [vcpkg](https://github.com/microsoft/vcpkg) 和[CMake](https://cmake.org/download)
2. 设置好`VCPKG_ROOT`路径，如 `$Env:VCPKG_ROOT="C:\vcpkg"`, `$Env:PATH="$Env:VCPKG_ROOT;$Env:PATH"`
3. 使用powershell执行`Generate.ps1`，即可将excel导出为csv并且生成对应的C++加载解析代码

### 生成解析代码

* `rapidcsv.h`是一个轻量级的CSV文件解析库，用于解析CSV文件
* `strconv.h`里实现了几个常用从字符串转换到具体类型的函数，如parseTo<int>("123")，并依赖了`abseil`
* 如果项目组开启了预编译头，比如`stdafx.h`，可以通过`--pch=stdafx.h`是源文件包含预编译头文件


## 配置详解


### 相关命令行参数

在命令行可以指定一些控制导出内容的参数，如：

* `--cpp_out` 输出的C++代码文件目录
* `--package` 指定名称空间
* `--gen_csv_parse` 是否生成代码中包含CSV数据加载函数，一般命名为`ParseRow()`
* `--source_file_encoding` 输出的源代码文件编码格式，默认为UTF-8
* `--file_asset` 指定输入的Excel文件或者目录
* `--file_skip` 指定不导出的Excel文件
* `--without_data` 不导出数据，只导出代码
* `--project_kind` 指定解析特定的字段类型，如`--project_kind=C`，只解析`C_`开头和不带kind的字段
* `--delim1` 指定第一级分隔符，默认为`|`
* `--delim2` 指定第二级分隔符，默认为`:`
* `--data_file_encoding` 输出的数据文件编码格式，默认为UTF-8
* `--out_data_format` 数据文件输出格式，默认为`csv`，可以选择`json`
* `--out_data_path` 输出的数据文件路径，默认为当前目录
