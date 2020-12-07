# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

CPP_MANAGER_METHOD_TEMPLATE = """
    // Load all configurations
    static void LoadAll();

    // Clear all configurations
    static void ClearAll();

    // Read content from an asset file
    static std::string ReadFileContent(const char* filepath);

    // default loader
    static std::function<std::string(const char*)> reader;
"""

CPP_CSV_TOKEN_TEMPLATE = """
static const char TAB_CSV_SEP = '%s';       // CSV field separator
static const char TAB_CSV_QUOTE = '%s';     // CSV field quote
static const char* TAB_ARRAY_DELIM = "%s";  // array item delimiter
static const char* TAB_MAP_DELIM1 = "%s";   // map item delimiter
static const char* TAB_MAP_DELIM2 = "%s";   // map key-value delimiter

"""

CPP_READER_ASSIGN = """
std::function<std::string(const char*)> %s::reader = %s::ReadFileContent;

"""

CPP_READ_FUNC_TEMPLATE = """
//Load content of an asset file'
std::string %s::ReadFileContent(const char* filepath)
{
    ASSERT(filepath != nullptr);
    FILE* fp = std::fopen(filepath, "rb");
    if (fp == NULL) {
        return "";
    }
    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    if (size == 0) {
        fclose(fp);
        return "";
    }
    std::string content;
    fread(&content[0], 1, size, fp);
    fclose(fp);
    return std::move(content);
}

"""

CPP_INSTANCE_METHOD_TEMPLATE = """
const %s* %s::Instance()
{
    ASSERT(%s != nullptr);
    return %s;
}
"""


CPP_GETDATA_METHOD_TEMPLATE = """
const std::vector<%s>* %s::GetData()
{
    ASSERT(%s != nullptr);
    return %s;
}

"""

CPP_LOAD_FUNC_TEMPLATE = """
// load %s data from csv file
int %s::Load(const char* filepath)
{
    vector<%s>* dataptr = new vector<%s>;
    std::string content = %s::reader(filepath);
    CSVReader reader(TAB_CSV_SEP, TAB_CSV_QUOTE);
    reader.Parse(content);
    auto rows = reader.GetRows();
    ASSERT(!rows.empty());
    for (size_t i = 0; i < rows.size(); i++)
    {
        auto row = rows[i];
        if (!row.empty())
        {
            %s item;
            %s::ParseFromRow(row, &item);
            dataptr->push_back(item);
        }
    }
    delete %s;
    %s = dataptr;
    return 0;
}
"""

CPP_KV_LOAD_FUNC_TEMPLATE = """
// load %s data from csv file
int %s::Load(const char* filepath)
{
    std::string content = %s::reader(filepath);
    CSVReader reader(TAB_CSV_SEP, TAB_CSV_QUOTE);
    reader.Parse(content);
    auto rows = reader.GetRows();
    ASSERT(!rows.empty());
    for (auto& row : rows)
    {
        if (!row.empty())
        {
            rows.push_back(row);
        }
    }
    %s* dataptr = new %s();
    %s::ParseFromRows(rows, dataptr);
    delete %s;
    %s = dataptr;
    return 0;
}
"""

CPP_GET_METHOD_TEMPLATE = """
const %s* %s::Get(%s)
{
    const vector<%s>* dataptr = GetData();
    ASSERT(dataptr != nullptr && dataptr->size() > 0);
    for (size_t i = 0; i < dataptr->size(); i++)
    {
        if (%s)
        {
            return &dataptr->at(i);
        }
    }
    return nullptr;
}
"""

CPP_GET_RANGE_METHOD_TEMPLATE = """
std::vector<const %s*> %s::GetRange(%s)
{
    const vector<%s>* dataptr = GetData();
    std::vector<const %s*> range;
    ASSERT(dataptr != nullptr && dataptr->size() > 0);
    for (size_t i = 0; i < dataptr->size(); i++)
    {
        if (%s)
        {
            range.push_back(&dataptr->at(i));
        }
    }
    return range;
}
"""
