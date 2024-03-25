# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


# array和map的分割字符
PredefDelim1 = '|'
PredefDelim2 = '='

PredefFieldNameRow = 0      # 这一行描述字段名称
PredefFieldTypeDefRow = 1   # 可选的字段类型定义行

PredefMetaSheet = "@meta"            # meta sheet默认名称
PredefClassName = "ClassName"        # meta sheet里指定生成的class名
PredefClassComment = "ClassComment"  # meta sheet里指定生成的class注释

PredefParseKVMode = 'KVMode'
PredefKVKeyName = 'Key'         # KV模式中的key所在列
PredefKVTypeName = 'Type'       # KV模式中的类型所在列
PredefKVValueName = 'Value'     # KV模式中的value所在列


PredefInnerTypeClass = "InnerTypeClass"
PredefInnerFieldName = "InnerFieldName"

OptionUniqueColumns = "UniqueFields"    # 值唯一的列名称

PredefProjectKindServer = "server"      # 服务端项目
PredefProjectKindClient = "client"      # 客户端项目
PredefProjectKindManager = "manager"    # 管理后台项目
