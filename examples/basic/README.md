## 基本用例演示

双击`导出CSharp.bat`文件即可导出C#代码，需要依赖Python, openpyxl, pymysql

## 配置详解

### 导出参数
* `--mode` 导入模式，excel或者mysql；
* `--import-args` 导入器的参数，例如excel模式需要输入文件或者目录名，mysql模式需要输入账号密码；
* `--generator` 生成器名称，目前支持`cpp-v1`, `cs-v1`, `go-v1`和`go-v2`；
* `--export-args` 导出参数，用来控制导出过程，如导出文件名称，是否不需要数据等；

### meta表里的配置

meta表里可以定义一些配置来控制如何导入
* `class-name`  生成的class名称	
* `class-comment`   生成的class注释
* `type-row` 定义每个字段类型的行，不填写则默认为第1行
* `name-row` 每个字段的名称所在行，不填写则默认为第2行
* `comment-row` 每个字段的注释行，不填写则默认为第3行
* `data-start-row` 数据从哪一行开始，不填写则默认为第4行
* `data-end-row` 数据从哪一行结束，不填写则默认为为最后一行
* `get-keys` 配置生成Get函数包含的参数（列），以逗号分隔，Get函数返回一个最匹配参数的配置项；
* `range-keys`  配置生成GetRange函数包含的参数（列），以逗号分隔，GetRange函数返回一组匹配参数的配置项；


