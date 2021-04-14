# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


CSHARP_MANAGER_TEMPLATE = """
public class %s 
{    
    public const char TABUGEN_CSV_SEP = '%s';           // CSV field delimiter
    public const char TABUGEN_CSV_QUOTE = '"';          // CSV field quote
    public const char TABUGEN_ARRAY_DELIM = '%s';       // array item delimiter
    public const char TABUGEN_MAP_DELIM1 = '%s';        // map item delimiter
    public const char TABUGEN_MAP_DELIM2 = '%s';        // map key-value delimiter
    
    // self-defined boolean value parse
    public static bool ParseBool(string text)
    {
        if (text == null || text.Length == 0) {
            return false;
        }
        return string.Equals(text, "1") ||
            string.Equals(text, "Y") || 
            string.Equals(text, "ON");
    }
"""
