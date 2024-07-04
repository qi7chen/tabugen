# Tabugen

Tabugen是一个配置导出和代码生成工具，主要用于游戏项目中简化业务开发数据抽象过程。

Tabugen导入Excel表格生成编程语言的结构体定义，导出CSV数据文件，并生成对应的CSV文件加载代码。


## Tabugen解决的几个痛点

写一个从excel表格导出csv和生成对应的业务代码的工具并不难，不好把控的是如何设计格式和流程让设计师和程序员之前更好的沟通，降低理解难道和配置踩坑，

Tabugen目前解决了日常使用中的几个痛点：


#### 痛点1 基本功能

从excel表格里导出结构体定义，并且把excel转为csv，这个是基本需求

比如我们有一个`HeroConfig.xlsx`文件，里面有如下内容：

 | #备注    | ID   | Name | Exp
 |---------|-------|------|-------
 | 流浪剑客 | 1001  | Sven | 2000
 | 冥界亚龙 | 1002  | Viper | 2500


* 第一行为字段名称，此名称会原样生成到结构体里；
* 以`#`开头的字段名在导出的时候会被忽略，可以用于配置一些说明信息；
* 第二行开始就是具体的数据内容

最后会生成代码如下：

```C++
struct HeroConfig {
    int ID;
    int Name;
    int Exp;
}
```

不需要单独配置一行来表达类型，也无需在字段名里加上类型前缀（当然要加也支持比如`INT_Exp`），Tabugen会自动根据数据行识别字段类型；

#### 痛点2 字段类型支持简单的数组和字典格式

 | #备注  | ID   | Name | Exp  | Buff | Drop
 |------|-------|------|------|------|------------
| 类型   | int  | string | int64 | int[] | <int,int>
 | 流浪剑客 | 1001  | Sven | 2000  | 1201,1202 | 2001=100,2002=300
 | 冥界亚龙 | 1002  | Viper | 2500 | 1302,1304 | 2001=150,2002=200

* 复杂的组合类型则需要单独用第二行来描述；
* `int[]`表示数组类型，默认使用竖线`|`分隔元素，格式如：`value1|value2|value3`，分隔符可以在cli里传递`--delim1`来指定；
* `<int,int>`表示字典类型，默认使用竖线`|`分隔元素，用`：`分隔键值，格式如: `key1:value1|key2:value2`，分隔符可以在cli里传递`--delim1` `--delim2`来指定；
* 生成的代码如下：

```C++
struct HeroConfig {
    int ID;
    string Name;
    int64 Exp;
    vector<int> Buff;
    map<int,int> Drop;
}
```

#### 痛点3 全局变量表的纵向解析格式

 | Key | Type | Vaue | # Desc
 |-----|------|------|------
 | Key1   | float  | 3.14              | 浮点数值
 | Key2   | string | SUCEE             | 显示文字
 | Key3   | bool   | 0                 | 功能开关
 | Key4   | int[] | 1 &#124; 2 &#124; 3 | 等级列表


会生成下面格式结构体

```
struct Global
{
    float Key1;
    string Key2;
    bool Key3;
    int[] Key4;
}
```

#### 痛点4，不同项目类型的区分导出

这是一个常见的需求，比如一个excel表格，某些字段只有客户端需要，某些字段只有服务器需要，
Tabugen的做法是通过前缀来实现

 | ID   | S_Field1 | C_Field2 | Field3
 |------|---------|-----------|--------
 | 1001 | 1       | 2         | 3


* 如果是仅服务器使用的字段，字段名的前缀加上`S_`，导出的时候指定选项`--project_kind=S`，这样会解析到不带前缀的和带`S_`前缀的字段；
* 如果是仅客户端使用的字段，字段名的前缀加上`C_`，导出的时候指定选项`--project_kind=C`，这样会解析到不带前缀的和带`C_`前缀的字段；


## 如何使用Tabugen(How to Use)


### 从pip导入

```
pip install tabugen
tabugen --asset_path=example.xlsx --cpp_out=MyConfig --package=config  --gen_csv_parse --source_file_encoding=utf_8_sig
```

这是推荐的方式，pip可以和项目的CI/CD更好的集成

### 使用PyInstaller从源码打包

* `git clone https://github.com/qi7chen/tabugen.git`
* `cd tabugen && python -m PyInstaller --name "tabugen" -F tabugen/__main__.py`


## 几种主流强类型语言的示例

请查看[examples](examples)目录下的示例工程：

* C++的示例 [examples/Cpp](examples/Cpp) 演示如何配合C++使用;
* C#的示例 [examples/CSharp](examples/CSharp) 演示如何配合C#(Unity)使用;
* Golang的示例 [examples/Go](examples/Go) 演示如何配合Golang使用;
* Java的示例 [examples/Java](examples/Java) 演示如何配合Java使用;
* 对于Python, JavaScript等动态语言，将Excel导出为json即可，指定选项`--out_data_format=json`
