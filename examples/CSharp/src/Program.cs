using System;
using System.IO;
using System.Collections.Generic;
using System.Text.Json;
using CsvHelper;

class Program
{
    public const char TABUGEN_CSV_SEP = ',';           // CSV field delimiter
    public const char TABUGEN_CSV_QUOTE = '"';          // CSV field quote

    

    static private string resRootPath = "";

    static string ReadJSONFile(string filename)
    {
        string filepath = Path.GetFullPath(string.Format("{0}/{1}", resRootPath, filename));
        StreamReader reader = new StreamReader(filepath);
        return reader.ReadToEnd();
    }

    static List<Dictionary<string, string>> ReadCSVRecords(string filename)
    {
        var filepath = Path.GetFullPath(string.Format("{0}/{1}", resRootPath, filename));
        var reader = new StreamReader(filepath);
        var csv = new CsvReader(reader, null);
        csv.GetRecord
        var lines = ReadFileToLines(filepath);
        var header = new List<string>();
        var records = new List<Dictionary<string, string>>();
        for (int i = 0; i < lines.Count; i++)
        {
            var line = lines[i];
            var row = ReadRowFromLine(line);
            if (i == 0)
            {
                header = row;
                continue;
            }
            var record = new Dictionary<string, string>();
            for (int j = 0; j < row.Count; j++)
            {
                record[header[j]] = row[j];
            }
            records.Add(record);
        }
        return records;
    }

    static Dictionary<string, string> RecordsToDict(List<Dictionary<string, string>> records)
    {
        var dict = new Dictionary<string, string>();
        for (var i = 0; i < records.Count; i++)
        {
            var record = records[i];
            dict.Add(record["Key"], record["Value"]);
        }
        return dict;
    }

    static void TestLoadGuideCSVConfig()
    {
        string filename = "newbie_guide_define.csv";
        var records = ReadCSVRecords(filename);
        for (int i = 0; i < records.Count; i++)
        {
            var val = new Config.NewbieGuideDefine();
            val.ParseFrom(records[i]);
            var output = JsonSerializer.Serialize(val);
            Console.WriteLine(output);
        }
    }

  
    static void TestLoadGuideJsonConfig()
    {
        var content = ReadJSONFile("newbie_guide_define.json");
        var confList = JsonSerializer.Deserialize<Config.NewbieGuideDefine[]>(content);
        for (int i = 0; i < confList.Length; i++)
        {
            var output = JsonSerializer.Serialize(confList[i]);
            Console.WriteLine(output);
        }

    }

    static void TestLoadSoldierCSVConfig()
    {
        string filename = "soldier_property_define.csv";
        var records = ReadCSVRecords(filename);
        for (int i = 0; i < records.Count; i++)
        {
            var val = new Config.SoldierPropertyDefine();
            val.ParseFrom(records[i]);
            var output = JsonSerializer.Serialize(val);
            Console.WriteLine(output);
        }
    }

    static void TestLoadSoldierJsonConfig()
    {
        var content = ReadJSONFile("soldier_property_define.json");
        var confList = JsonSerializer.Deserialize<Config.SoldierPropertyDefine[]>(content);
        for (int i = 0; i < confList.Length; i++)
        {
            var val = confList[i];
            var output = JsonSerializer.Serialize(val);
            Console.WriteLine(output);
        }
    }


    static void TestLoadGlobalCSVConfig()
    {
        string filename = "global_property_define.csv";
        var records = ReadCSVRecords(filename);
        var kvMap = RecordsToDict(records);
        var instance = new Config.GlobalPropertyDefine();
        instance.ParseFrom(kvMap);

        var output = JsonSerializer.Serialize(instance);
        Console.WriteLine(output);
    }

    static void TestLoadGlobalJsonConfig()
    {
        var content = ReadJSONFile("global_property_define.json");

        var instance = JsonSerializer.Deserialize<Config.GlobalPropertyDefine>(content);
        var output = JsonSerializer.Serialize(instance);
        Console.WriteLine(output);
    }


    static void TestLoadBoxCSVConfig()
    {
        string filename = "box_probability_define.csv";
        var records = ReadCSVRecords(filename);
        for (int i = 0; i < records.Count; i++)
        {
            var val = new Config.BoxProbabilityDefine();
            val.ParseFrom(records[i]);
            var output = JsonSerializer.Serialize(val);
            Console.WriteLine(output);
        }
    }

    static void TestLoadBoxJsonConfig()
    {
        var content = ReadJSONFile("box_probability_define.json");

        var confList = JsonSerializer.Deserialize<Config.BoxProbabilityDefine[]>(content);
        for (int i = 0; i < confList.Length; i++)
        {
            var val = confList[i];
            var output = JsonSerializer.Serialize(val);
            Console.WriteLine(output);
        }
    }

    static void Main(string[] args)
    {
        string rootPath = "../../../../../datasheet/res";
        if (args.Length > 1)
        {
            rootPath = args[1];
        }

        resRootPath = rootPath;

        try
        {
            TestLoadGuideCSVConfig();
            Console.WriteLine("-----------------------------------------------");
            TestLoadGuideJsonConfig();

            Console.WriteLine("-----------------------------------------------");

            TestLoadSoldierCSVConfig();
            Console.WriteLine("-----------------------------------------------");
            TestLoadSoldierJsonConfig();

            Console.WriteLine("-----------------------------------------------");

            TestLoadGlobalCSVConfig();
            Console.WriteLine("-----------------------------------------------");
            TestLoadGlobalJsonConfig();

            Console.WriteLine("-----------------------------------------------");

            TestLoadBoxCSVConfig();
            Console.WriteLine("-----------------------------------------------");
            TestLoadBoxJsonConfig();
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.ToString());
        }
    }
}

