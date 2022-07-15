"""
Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
Distributed under the terms and conditions of the Apache License.
See accompanying files LICENSE.
"""

# array和map的分割字符
PredefDelim1 = '|'
PredefDelim2 = '='

PredefFieldNameRow = 0      # 这一行描述字段名称
PredefFieldTypeRow = 1      # 这一行描述类型
PredefCommentRow = 2        # 这一行描述注释文字
PredefDataStartRow = 3      # 数据从这一行开始

PredefMetaSheet = "@meta"                   # meta sheet名称
PredefClassName = "ClassName"              # 生成的class名称
PredefClassComment = "ClassComment"        # 生成的class注释

PredefParseKVMode = "KVMode"   # 是否是KV模式
PredefKeyColumn = 0             # KV模式中的key所在列
PredefValueTypeColumn = 1       # KV模式中的value类型所在列
PredefValueColumn = 2           # KV模式中的value所在列
PredefCommentColumn = 3         # KV模式中的注释所在列

PredefInnerTypeClass = "InnerTypeClass"
PredefInnerFieldName = "InnerFieldName"

OptionUniqueColumns = "UniqueFields"    # 值唯一的列名称
