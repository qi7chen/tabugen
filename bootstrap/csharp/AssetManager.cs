using System;
using System.IO;
using UnityEngine;

public class AssetsManager
{
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
}