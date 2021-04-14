# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


CPP_CSV_TOKEN_TEMPLATE = """// separator used by Tabular
static const char TABULAR_CSV_SEP = '%s';       // CSV field separator
static const char TABULAR_CSV_QUOTE = '%s';     // CSV field quote
static const char* TABULAR_ARRAY_DELIM = "%s";  // array item delimiter
static const char* TABULAR_MAP_DELIM1 = "%s";   // map item delimiter
static const char* TABULAR_MAP_DELIM2 = "%s";   // map key-value delimiter

"""
