using System;
using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;

#if UNITY 
using UnityEngine;
using UnityEngine.Networking;
#endif

namespace CSharpDemo
{
    class Program
    {
#if UNITY        
        public static void GetStreamingContent(string path, Action<string> cb)
        {
            string filePath = Path.Combine(Application.streamingAssetsPath, path);
    #if UNITY_ANDROID
            StartCoroutine(LoadAsset(filePath, cb));
    #else
            using (StreamReader reader = new StreamReader(filePath))
            {
                cb(reader.ReadToEnd());
            }
    #endif
        }

        IEnumerator LoadAsset(string filePath, Action<string> cb)
        {
            using (UnityWebRequest www = UnityWebRequest.Get(filePath))
            {
                yield return www.SendWebRequest();
                if (www.isNetworkError || www.isHttpError)
                {
                    Debug.LogErrorFormat("LoadAsset: error: {0} {1}",  www.error, filePath);
                    cb(null);
                }
                else
                {
                    cb(www.downloadHandler.data);
                }
            }
        }
#endif         
    
        static void ReadFileContent(string filepath, Action<string> cb)
        {
#if UNITY
            GetStreamingContent(filepath, cb);
#else
            string path = string.Format("../res/{0}", filepath);
            StreamReader reader = new StreamReader(path);
            var content = reader.ReadToEnd();
            cb(content);    
#endif
        }
        
        static void TestLoadCSV()
        {
            string filename = "global_property_define.csv";
            string filepath = string.Format("../res/{0}", filename);
            string content = Config.AutogenConfigManager.ReadFileContent(filepath);
            var lines = Config.AutogenConfigManager.ReadTextToLines(content);
            var rows = new List<List<string>>();
            for (int i = 0; i < lines.Count; i++)
            {
                var row = Config.AutogenConfigManager.ReadRecordFromLine(lines[i]);
                rows.Add(row);
            }
            var instance = new Config.GlobalPropertyDefine();
            instance.ParseFromRows(rows);

            Console.WriteLine(instance.FreeCompleteSeconds);
            Console.WriteLine(instance.SpawnLevelLimit);
            Console.WriteLine(instance.FirstRechargeReward);
        }

        static void TestLoadJSON()
        {
            string filename = "global_property_define.json";
            string filepath = string.Format("../res/{0}", filename);
            StreamReader reader = new StreamReader(filepath);
            var content = reader.ReadToEnd();

            var conflist = JsonConvert.DeserializeObject<Config.GlobalPropertyDefine>(content);
            var text = JsonConvert.SerializeObject(conflist);
            Console.WriteLine(text);
        }
        
        static void Main(string[] args)
        {
            try
            {
                TestLoadCSV();
                TestLoadJSON();
            }
            catch(Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
        }
    }
}
