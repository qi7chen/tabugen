using Config;
using nietras.SeparatedValues;

class DataFrame : IDataFrame
{
    private Dictionary<string, int> headers = new Dictionary<string, int>();
    private List<List<string>> rows = new List<List<string>>();
    private Dictionary<string, string> keyFields = new Dictionary<string, string>();

    public DataFrame(string path)
    {
        var sep = new Sep(',');
        using var reader = sep.Reader().FromFile(path);
        for (var i = 0; i < reader.Header.ColNames.Count; i++)
        {
            var name = reader.Header.ColNames[i];
            if (!name.StartsWith("#")) {
                headers[name] = i;
            }
        }
        foreach (var row in reader)
        {
            var list = new List<string>();
            for (var i = 0; i < row.ColCount; i++) {
                list.Add(row[i].ToString());
            }
            rows.Add(list);
        }
    }

    public int ColumnCount
    {
        get => headers.Count;
    }

    public int RowCount
    {
        get => rows.Count;
    }

    public bool HasColumn(string name)
    {
        return headers.ContainsKey(name);
    }

    public string GetRowCell(string name, int index)
    {
        if (!headers.ContainsKey(name)) {
            return "";
        }
        var i = headers[name];
        return rows[index][i];
    }

    public string GetKeyField(string key)
    {
        string result;
        if (keyFields.TryGetValue(key, out result)) {
            return result;
        } else {
            return "";
        }
    }

    public void LoadKeyValueFields()
    {
        keyFields.Clear();
        for (int i = 0; i < RowCount; i++)
        {
            var key = GetRowCell("Key", i);
            var value = GetRowCell("Value", i);
            keyFields.Add(key, value);
        }
    }
}
