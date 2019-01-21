using System;
using System.IO;

namespace CSharpDemo
{
    class Program
    {
#ifdef UNITY        
        public static void GetStreamingContent(string path, Action<string> cb)
        {
            string filePath = Path.Combine(Application.streamingAssetsPath, path);
    #ifdef UNITY_ANDROID
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
#ifdef UNITY
            GetStreamingContent(filepath, cb);
#else
            string path = string.Format("../../{0}", filepath);
            StreamReader reader = new StreamReader(path);
            var content = reader.ReadToEnd();
            cb(content);    
#endif
        }

        static void Main(string[] args)
        {
            Config.AutogenConfigManager.reader = ReadFileContent;
            Config.AutogenConfigManager.LoadAllConfig(() => 
            {
                Console.WriteLine("OK");
            });
        }
    }
}
