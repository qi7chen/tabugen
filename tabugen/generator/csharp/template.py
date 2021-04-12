# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


CSHARP_MANAGER_TEMPLATE = """
public class %s 
{    
    public const char TAB_CSV_SEP = '%s';           // CSV field delimiter
    public const char TAB_CSV_QUOTE = '"';          // CSV field quote
    public const char TAB_ARRAY_DELIM = '%s';       // array item delimiter
    public const char TAB_MAP_DELIM1 = '%s';        // map item delimiter
    public const char TAB_MAP_DELIM2 = '%s';        // map key-value delimiter
    

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

    // 读取文件内容
    public static string ReadFileContent(string filepath)
    {
        StreamReader reader = new StreamReader(filepath);
        return reader.ReadToEnd();
    }
    
    // 把内容分行
    public static List<string> ReadTextToLines(string content)
    {
        List<string> lines = new List<string>();
        using (StringReader reader = new StringReader(content))
        {
            string line;
            while ((line = reader.ReadLine()) != null)
            {
                lines.Add(line);
            }
        }
        return lines;
    }

    // 从一行读取record
    public static List<string> ReadRecordFromLine(string line)
    {
        List<string> row = new List<string>();
        int pos = 0;
        while (pos < line.Length)
        {
            string field = "";
            pos = ParseNextColumn(line, pos, out field);
            row.Add(field.Trim());
            if (pos < 0)
            {
                break;
            }
        }
        return row;
    }
        
    // 解析下一个column
    public static int ParseNextColumn(string line, int start, out string field)
    {
        bool in_quote = false;
        if (line[start] == TAB_CSV_QUOTE)
        {
            in_quote = true;
            start++;
        }
        int pos = start;
        for (; pos < line.Length; pos++)
        {
            if (in_quote && line[pos] == TAB_CSV_QUOTE)
            {
                if (pos + 1 < line.Length && line[pos + 1] == TAB_CSV_SEP)
                {
                    field = line.Substring(start, pos - start);
                    return pos + 2;
                }
                else
                {
                    field = line.Substring(start, pos - start);
                    return pos + 1;
                }
            }
            if (!in_quote && line[pos] == TAB_CSV_SEP)
            {
                field = line.Substring(start, pos - start);
                return pos + 1;
            }
        }
        field = line.Substring(start, pos);
        return -1;
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
