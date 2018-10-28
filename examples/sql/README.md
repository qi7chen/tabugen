## SQL模式

双击`导出Go.bat`文件即可导出Go代码，需要依赖Python, openpyxl, pymysql

## 配置格式

### 导出参数
`--host` MySQL数据库服务器地址；
`--port` MySQL数据库服务器端口；
`--user` 连接MySQL数据库的账号；
`--passwd` 账号密码；
`--db`  指定一个数据库名称，为空则会拉取所有库的信息；
`--table` 指定一个表名称，为空则会拉取本库下所有table信息；

### meta表里的配置