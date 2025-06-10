using System;
using System.Text.Json;


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

    static DataFrame ReadCSVDataFrame(string filename)
    {
        var filepath = Path.GetFullPath(string.Format("{0}/{1}", resRootPath, filename));
        return new DataFrame(filepath);
    }
    

    static void TestLoadGuideCSVConfig()
    {
        var dataframe = ReadCSVDataFrame("newbie_guide.csv");
        for (int i = 0; i < dataframe.RowCount; i++)
        {
            var val = new Config.NewbieGuide();
            val.ParseRow(dataframe, i);
            var output = JsonSerializer.Serialize(val);
            Console.WriteLine(output);
        }
    }


    static void TestLoadGuideJsonConfig()
    {
        var content = ReadJSONFile("newbie_guide.json");
        var confList = JsonSerializer.Deserialize<Config.NewbieGuide[]>(content);
        for (int i = 0; i < confList.Length; i++)
        {
            var output = JsonSerializer.Serialize(confList[i]);
            Console.WriteLine(output);
        }
    }

    static void TestLoadSoldierCSVConfig()
    {
        var dataframe = ReadCSVDataFrame("soldier_define.csv");
        for (int i = 0; i < dataframe.RowCount; i++)
        {
            var val = new Config.SoldierDefine();
            val.ParseRow(dataframe, i);
            var output = JsonSerializer.Serialize(val);
            Console.WriteLine(output);
        }
    }

    static void TestLoadSoldierJsonConfig()
    {
        var content = ReadJSONFile("soldier_define.json");
        var confList = JsonSerializer.Deserialize<Config.SoldierDefine[]>(content);
        for (int i = 0; i < confList.Length; i++)
        {
            var val = confList[i];
            var output = JsonSerializer.Serialize(val);
            Console.WriteLine(output);
        }
    }


    static void TestLoadGlobalCSVConfig()
    {
        var dataframe = ReadCSVDataFrame("global_define.csv");
        dataframe.LoadKeyValueFields();
        var instance = new Config.GlobalDefine();
        instance.ParseFrom(dataframe);

        var output = JsonSerializer.Serialize(instance);
        Console.WriteLine(output);
    }

    static void TestLoadGlobalJsonConfig()
    {
        var content = ReadJSONFile("global_define.json");
        var instance = JsonSerializer.Deserialize<Config.GlobalDefine>(content);
        var output = JsonSerializer.Serialize(instance);
        Console.WriteLine(output);
    }


    static void TestLoadBoxCSVConfig()
    {
        var dataframe = ReadCSVDataFrame("item_box_define.csv");
        for (int i = 0; i < dataframe.RowCount; i++)
        {
            //var val = new Config.BoxProbabilityDefine();
            //val.ParseFrom(records[i]);
            //var output = JsonSerializer.Serialize(val);
            //Console.WriteLine(output);
        }
    }

    static void TestLoadBoxJsonConfig()
    {
        var content = ReadJSONFile("box_probability_define.json");

        //var confList = JsonSerializer.Deserialize<Config.BoxProbabilityDefine[]>(content);
        //for (int i = 0; i < confList.Length; i++)
        //{
        //    var val = confList[i];
        //    var output = JsonSerializer.Serialize(val);
        //    Console.WriteLine(output);
        //}
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

