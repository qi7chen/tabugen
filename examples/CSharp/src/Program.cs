using System;
using System.IO;
using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;


namespace CSharpDemo
{
    class Program
    {
        public const char TABUGEN_CSV_SEP = ',';           // CSV field delimiter
        public const char TABUGEN_CSV_QUOTE = '"';          // CSV field quote
        public const char TABUGEN_ARRAY_DELIM = ',';       // array item delimiter
        public const char TABUGEN_MAP_DELIM1 = ';';        // map item delimiter
        public const char TABUGEN_MAP_DELIM2 = '=';        // map key-value delimiter

        static List<string> ReadFileToLines(string filepath)
        {
            StreamReader r = new StreamReader(filepath);
            string content = r.ReadToEnd();
            r.Close();
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

        public static int ParseNextColumn(string line, int start, out string field)
        {
            bool in_quote = false;
            if (line[start] == TABUGEN_CSV_QUOTE)
            {
                in_quote = true;
                start++;
            }
            int pos = start;
            for (; pos < line.Length; pos++)
            {
                if (in_quote && line[pos] == TABUGEN_CSV_QUOTE)
                {
                    if (pos + 1 < line.Length && line[pos + 1] == TABUGEN_CSV_SEP)
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
                if (!in_quote && line[pos] == TABUGEN_CSV_SEP)
                {
                    field = line.Substring(start, pos - start);
                    return pos + 1;
                }
            }
            field = line.Substring(start, pos);
            return -1;
        }

        static void TestLoadGuideCSVConfig(string rootPath)
        {
            string filename = "newbie_guide_define.csv";
            string filepath = string.Format("{0}/res/{1}", rootPath, filename);
            var lines = ReadFileToLines(filepath);
            var list = new Config.NewbieGuideDefine[lines.Count];
            for (int i = 0; i < lines.Count; i++)
            {
                var row = ReadRecordFromLine(lines[i]);
                var obj = new Config.NewbieGuideDefine();
                obj.ParseFromRow(row);
                list[i] = obj;
                Console.WriteLine(JsonSerializer.Serialize<Config.NewbieGuideDefine>(obj));
            }
        }

        static void TestLoadGuideJsonConfig(string rootPath)
        {
            string filename = "newbie_guide_define.json";
            string filepath = string.Format("{0}/res/{1}", rootPath, filename);
            StreamReader reader = new StreamReader(filepath);
            var content = reader.ReadToEnd();

            var conflist = JsonSerializer.Deserialize<Config.NewbieGuideDefine[]>(content);
            for (int i = 0; i < conflist.Length; i++)
            {
                var text = JsonSerializer.Serialize(conflist[i]);
                Console.WriteLine(text);
            }
            
        }

        static void TestLoadSoldierCSVConfig(string rootPath)
        {
            string filename = "soldier_property_define.csv";
            string filepath = Path.GetFullPath(string.Format("{0}/res/{1}", rootPath, filename));
            Console.WriteLine("load file {0}", filepath);
            var lines = ReadFileToLines(filepath);
            var list = new Config.SoldierPropertyDefine[lines.Count];
            for(int i = 0; i < list.Length; i++)
            {
                var row = ReadRecordFromLine(lines[i]);
                var item = new Config.SoldierPropertyDefine();
                item.ParseFromRow(row);
                list[i] = item;
                Console.WriteLine(JsonSerializer.Serialize<Config.SoldierPropertyDefine>(item));
            }
        }

        static void TestLoadSoldierJsonConfig(String rootPath)
        {
            string filename = "soldier_property_define.json";
            string filepath = Path.GetFullPath(string.Format("{0}/res/{1}", rootPath, filename));
            Console.WriteLine("load file {0}", filepath);
            StreamReader reader = new StreamReader(filepath);
            var content = reader.ReadToEnd();
            var conflist = JsonSerializer.Deserialize<Config.SoldierPropertyDefine[]>(content);
            var text = JsonSerializer.Serialize<Config.SoldierPropertyDefine[]>(conflist);
            Console.WriteLine(text);
        }        


      static void TestLoadGlobalCSVConfig(string rootPath)
        {
            string filename = "global_property_define.csv";
            string filepath = string.Format("{0}/res/{1}", rootPath, filename);
            var lines = ReadFileToLines(filepath);
            var rows = new List<List<string>>();
            for (int i = 0; i < lines.Count; i++)
            {
                var row = ReadRecordFromLine(lines[i]);
                rows.Add(row);
            }
            var instance = new Config.GlobalPropertyDefine();
            instance.ParseFromRows(rows);

            Console.WriteLine(JsonSerializer.Serialize(instance));
        }

        static void TestLoadGlobalJsonConfig(string rootPath)
        {
            string filename = "global_property_define.json";
            string filepath = string.Format("{0}/res/{1}", rootPath, filename);
            StreamReader reader = new StreamReader(filepath);
            var content = reader.ReadToEnd();

            var glob = JsonSerializer.Deserialize<Config.GlobalPropertyDefine>(content);
            var text = JsonSerializer.Serialize(glob);
            Console.WriteLine(text);
        }


        static void TestLoadBoxCSVConfig(string rootPath)
        {
            string filename = "box_probability_define.csv";
            string filepath = string.Format("{0}/res/{1}", rootPath, filename);
            var lines = ReadFileToLines(filepath);
            var list = new Config.BoxProbabilityDefine[lines.Count];
            for (int i = 0; i < list.Length; i++)
            {
                var row = ReadRecordFromLine(lines[i]);
                var item = new Config.BoxProbabilityDefine();
                item.ParseFromRow(row);
                list[i] = item;
                Console.WriteLine(JsonSerializer.Serialize(item));
            }
        }

        static void TestLoadBoxJsonConfig(string rootPath)
        {
            string filename = "box_probability_define.json";
            string filepath = string.Format("{0}/res/{1}", rootPath, filename);
            StreamReader reader = new StreamReader(filepath);
            var content = reader.ReadToEnd();

            var conflist = JsonSerializer.Deserialize<Config.BoxProbabilityDefine[]>(content);
            var text = JsonSerializer.Serialize(conflist);
            Console.WriteLine(text);
        }

        static void Main(string[] args)
        {
            string rootPath = "..";
            if (args.Length > 1) {
                rootPath = args[1];
            }
            try
            {
                TestLoadGuideCSVConfig(rootPath);
                Console.WriteLine("-----------------------------------------------");
                TestLoadGuideJsonConfig(rootPath);

                Console.WriteLine("-----------------------------------------------");
                
                TestLoadSoldierCSVConfig(rootPath);
                Console.WriteLine("-----------------------------------------------");
                TestLoadSoldierJsonConfig(rootPath);

                Console.WriteLine("-----------------------------------------------");

                TestLoadGlobalCSVConfig(rootPath);
                Console.WriteLine("-----------------------------------------------");
                TestLoadGlobalJsonConfig(rootPath);                

                Console.WriteLine("-----------------------------------------------");

                TestLoadBoxCSVConfig(rootPath);
                Console.WriteLine("-----------------------------------------------");
                TestLoadBoxJsonConfig(rootPath); 
            }
            catch(Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
        }
    }
}
