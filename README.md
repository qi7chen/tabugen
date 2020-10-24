# TAKSi

老司机，带你飞

TAKSi导入Excel表格生成编程语言的结构体定义，导出CSV数据文件，并生成对应的CSV文件加载代码，旨在简化业务开发中的数据抽象过程。


# TAKSi特性

* 支持主流静态语言(C++、C#、Java、Go)的代码生成

* 支持配置简单数组和字典类型

* 自动生成CSV数据加载代码


# 如何使用TAKSi

## 编辑一个excel文件

    将excel表格的数据sheet按第1行为字段名称、第2行为数据类型、第3行为注释，从第4行开始为数据内容的格式编辑，如下表：
    

Name                |  DamagePerSec         |  Level      |  Cost
--------------------|-----------------------|-------------|--------------------------------------------
string              |  int                  |  int16      |  map<string, int>
名称                |  每秒伤害             |  等级       |  升级消耗
Marine              |  100                  |  1          | Food=100;Steel=200
Marine              |  150                  |  2          | Food=500;Steel=1000
Marine              |  200                  |  3          | Food=1000;Steel=2000
Marine              |  300                  |  4          | Food=2000;Steel=5000
Marine              |  500                  |  5          | Food=5000;Steel=10000



# 各种语言的示例

    请查看examples目录下的TAKSi导出示例：

* [C++的示例](examples/Cpp) 演示如何配合C++使用;
* [C#的示例](examples/CSharp) 演示如何配合C#(Unity)使用;
* [Golang的示例](examples/Go) 演示如何配合Golang使用;
* [Java的示例](examples/Java) 演示如何配合Java使用;
* 对于python, javascript, lua等动态语言，将excel导出为json即可


# 如何打包TAKSi成执行档

Windows上没有默认安装Python环境，可以使用PyInstaller将TAKSi打包成执行档发布

```
pip install -r requirements.txt
pyinstaller -F --name=taksi taksi\cli.py
```

# TO-DO

* 优化excel导出速度；
* 提供[WebGUI](https://adminlte.io/preview)后台，实现配置数据查看、编辑，方便非技术人员进行数值更改、验证；
