## 使用Tabugen导出C#


## 示例

### 如何执行

1. 需要安装[.net SDK](https://dotnet.microsoft.com/)
2. 使用powershell执行`Generate.ps1`，即可将excel导出为csv并且生成对应的C#加载解析代码
3. 可选，安装IDE调试环境，[Visual Studio](https://www.visualstudio.com)或者[Jetbrains Rider](https://www.jetbrains.com/rider/)

### 生成解析代码

* `Conv.cs`里实现了几个常用从字符串转换到具体类型的函数，如parseTo<int>("123")，并依赖了`abseil`
* `DataFrame.csv`是具体的表格数据IO实现，应用
* CSV解析用到了[Sep](https://github.com/nietras/Sep)

### meta表里的配置

在excel文件的@meta表里可以定义一些配置来控制如何导入，如：

* `ClassName`  生成的class名称
* `ClassComment`   生成的class注释
* `InnerTypeClass` 嵌入类型的class名称
* `InnerFieldName` 嵌入类型的成员变量名
* `UniqueFields` 对于这些字段，导出的时候会检查每行的数据值是否有重复

### 相关命令行参数

在命令行可以指定一些控制导出内容的参数，如：

* `--csharp_out` 输出的C#代码文件名称
* `--package` 指定C#命名空间
* `--source_file_encoding` 输出的源代码文件编码格式，默认为UTF-8
* `--gen_csv_parse` 是否包含CSV数据加载代码
* `--with-conv` 生成`Conv.cs`文件

