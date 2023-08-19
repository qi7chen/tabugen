## 使用Tabugen导出C++


## 示例

### 如何编译

1. 需要安装[Visual C++](https://www.visualstudio.com)和 [vcpkg](https://github.com/microsoft/vcpkg) 和[CMake](https://cmake.org/download)
2. 再用`vcpkg`安装[boost](https://www.boost.org)
3. 使用powershell执行`Generate.ps1`，即可将excel导出为csv并且生成对应的C++加载解析代码

### 生成解析代码

如果指定了生成解析代码，解析函数会需要用到3类函数

* 将字符串转换为数值类型(int/float)的函数；
* 根据格式拼接字符串的`sprintf`函数；
* 根据分隔符分割字符串的`split`函数；

这些细节都被实现在`Conv.h`里，在`--with-conv`选项开启的时候，会生成`Conv.h`文件，文件默认使用boost的实现。
如果不想引入boost，可以自己实现`Conv.h`里的API，并在导出的时候不指定`--with-conv`选项。


## 配置详解


### meta表里的配置

在excel文件的`@meta`表里可以定义一些配置来控制如何导入，如：

在excel文件的`@meta`表里可以定义一些配置来控制如何导入，如：

* `ClassName`  生成的class名称
* `ClassComment`   生成的class注释
* `InnerTypeClass` 嵌入类型的class名称
* `InnerFieldName` 嵌入类型的成员变量名
* `UniqueFields` 对于这些字段，导出的时候会检查每行的数据值是否有重复


### 相关命令行参数

在命令行可以指定一些控制导出内容的参数，如：

* `--cpp_out` 输出的C++代码文件名称
* `--package` 指定C++命名空间
* `--source_file_encoding` 输出的源代码文件编码格式，默认为UTF-8
* `--with_csv_parse` 是否包含CSV数据加载代码
* `--with-conv` 生成`Conv.h`文件
* `--cpp_pch` 包含的预编译头文件
* `--extra_cpp_include` 额外包含的C++头文件




