## 使用Tabugen导出C++


## 示例

### 如何编译

1. 需要安装[vcpkg](https://github.com/microsoft/vcpkg) 和[CMake](https://cmake.org/download)
2. 项目依赖了[abseil](https://github.com/abseil/abseil-cpp) 库，需要通过vcpkg配置对应的环境
3. 执行`make genearate`，即可导出默认选项的C++代码
4. 执行`make output`导出csv和json
5. 执行`make run`，即可编译和运行对应的C++项目


## 配置详解


### meta表里的配置

在excel文件的@meta表里可以定义一些配置来控制如何导入，如：

在excel文件的@meta表里可以定义一些配置来控制如何导入，如：

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
* `--cpp_pch` 包含的预编译头文件
* `--extra_cpp_include` 额外包含的C++头文件

### 基础代码库

* 目前解析array和map依赖`SplitString`函数，定义在`StringUtil.h`里
* 数字和字符串之间的转换依赖`parseType(value)`函数，定义在`Conv.h`里

通过`--extra_cpp_include`参数传入你自己的头文件，可以覆盖默认的代码实现；


