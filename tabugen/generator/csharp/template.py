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
    

    public static bool ParseBool(string text)
    {
        if (text.Length > 0)
        {
            return string.Equals(text, "1") ||
                string.Equals(text, "y", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(text, "on", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(text, "yes", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(text, "true", StringComparison.OrdinalIgnoreCase);
        }
        return false;
    }
"""

CSHARP_RANGE_METHOD_TEMPLATE = """
    // get a range of items by key
    public static List<%s> GetRange(%s)
    {
        var range = new List<%s>();
        foreach (%s item in Data)
        {
            if (%s)
            {
                range.Add(item);
            }
        }
        return range;
    }
"""

CSHARP_GET_METHOD_TEMPLATE = """
    // get an item by key
    public static %s Get(%s)
    {
        foreach (%s item in Data)
        {
            if (%s)
            {
                return item;
            }
        }
        return null;
    }
"""

CSHARP_LOAD_METHOD_TEMPLATE = """
    public static void LoadFromLines(List<string> lines)
    {
        var list = new %s[lines.Count];
        for(int i = 0; i < lines.Count; i++)
        {
            var row = %s.ReadRecordFromLine(lines[i]);
            var obj = new %s();
            obj.ParseFromRow(row);
            list[i] = obj;
        }
        Data = list;
    }
"""

CSHARP_LOAD_FROM_METHOD_TEMPLATE = """
public static void LoadFromLines(List<string> lines)
{
    var rows = new List<List<string>>();
    for(int i = 0; i < lines.Count; i++)
    {
        var row = %s.ReadRecordFromLine(lines[i]);
        rows.Add(row);
    }
    Instance = new %s();
    Instance.ParseFromRows(rows);
}
"""
