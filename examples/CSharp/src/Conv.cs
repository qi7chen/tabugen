// Copyright (C) 2024-present qi7chen@github All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.


namespace Config
{

public class Conv
{
    public static string TabDelim1 = "|";
    public static string TabDelim2 = ":";

    public static bool ParseBool(string s)
    {
        if (string.IsNullOrEmpty(s))
        {
            return false;
        }
        if (s == "1" || s == "y" || s == "Y" || s == "on" || s == "On" || s == "ON")
        {
            return true;
        }
        bool result = false;
        bool.TryParse(s, out result);
        return result;
    }

    public static byte ParseByte(string s)
    {
        if (string.IsNullOrEmpty(s))
        {
            return 0;
        }
        byte result = 0;
        byte.TryParse(s, out result);
        return result;
    }

    public static sbyte ParseSbyte(string s)
    {
        if (string.IsNullOrEmpty(s))
        {
            return 0;
        }
        sbyte result = 0;
        sbyte.TryParse(s, out result);
        return result;
    }

    public static short ParseShort(string s)
    {
        if (string.IsNullOrEmpty(s))
        {
            return 0;
        }
        short result = 0;
        short.TryParse(s, out result);
        return result;
    }

    public static ushort ParseUShort(string s)
    {
        if (string.IsNullOrEmpty(s))
        {
            return 0;
        }
        ushort result = 0;
        ushort.TryParse(s, out result);
        return result;
    }

    public static int ParseInt(string s)
    {
        if (string.IsNullOrEmpty(s))
        {
            return 0;
        }
        int result = 0;
        int.TryParse(s, out result);
        return result;
    }

    public static uint ParseUInt(string s)
    {
        if (string.IsNullOrEmpty(s))
        {
            return 0;
        }
        uint result = 0;
        uint.TryParse(s, out result);
        return result;
    }

    public static long ParseLong(string s)
    {
        if (string.IsNullOrEmpty(s))
        {
            return 0;
        }
        long result = 0;
        long.TryParse(s, out result);
        return result;
    }

    public static ulong ParseULong(string s)
    {
        if (string.IsNullOrEmpty(s))
        {
            return 0;
        }
        ulong result = 0;
        ulong.TryParse(s, out result);
        return result;
    }

    public static float ParseFloat(string s)
    {
        if (string.IsNullOrEmpty(s))
        {
            return 0;
        }
        float result = 0;
        float.TryParse(s, out result);
        return result;
    }

    public static double ParseDouble(string s)
    {
        if (string.IsNullOrEmpty(s))
        {
            return 0;
        }
        double result = 0;
        double.TryParse(s, out result);
        return result;
    }

    public static List<T> ParseArray<T>(string s) where T : notnull
        {
        var list = new List<T>();
        var parts = s.Split(TabDelim1, StringSplitOptions.RemoveEmptyEntries);
        for (int i = 0; i < parts.Length; i++)
        {
            if (parts[i].Length > 0)
            {
                T v = (T)Convert.ChangeType(parts[i], typeof(T));
                list.Add(v);
            }
        }
        return list;
    }

    public static Dictionary<K,V> ParseMap<K,V>(string s) where K: notnull
    {
        var dict = new Dictionary<K, V>();
        var parts = s.Split(TabDelim1, StringSplitOptions.RemoveEmptyEntries);
        for (int i = 0; i < parts.Length; i++)
        {
            var pair = parts[i].Split(TabDelim2, StringSplitOptions.RemoveEmptyEntries);
            if (pair.Length == 2)
            {
                K key = (K)Convert.ChangeType(pair[0], typeof(K));
                V val = (V)Convert.ChangeType(pair[1], typeof(V));
                dict[key] = val;
            }
        }
        return dict;
    }
}

} // namespace Config
