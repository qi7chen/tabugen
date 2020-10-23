# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


CSHARP_MANAGER_TEMPLATE = """
public class %s 
{    
    public const char CSV_SEP = '%s';           // CSV field delimiter
    public const char CSV_QUOTE = '"';          // CSV field quote
    public const char TAKSI_ARRAY_DELIM = '%s'; 
    public const char TAKSI_MAP_DELIM1 = '%s';
    public const char TAKSI_MAP_DELIM2 = '%s';
    
    public delegate void ContentReader(string filepath, Action<string> callback);
    public static ContentReader reader = ReadFileContent;

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
    public static void ReadFileContent(string filepath, Action<string> cb)
    {
        StreamReader reader = new StreamReader(filepath);
        var content = reader.ReadToEnd();
        cb(content);
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
        if (line[start] == CSV_QUOTE)
        {
            in_quote = true;
            start++;
        }
        int pos = start;
        for (; pos < line.Length; pos++)
        {
            if (in_quote && line[pos] == CSV_QUOTE)
            {
                if (pos + 1 < line.Length && line[pos + 1] == CSV_SEP)
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
            if (!in_quote && line[pos] == CSV_SEP)
            {
                field = line.Substring(start, pos - start);
                return pos + 1;
            }
        }
        field = line.Substring(start, pos);
        return -1;
    }

"""
