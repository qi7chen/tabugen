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

CPP_LOAD_FUNC_TEMPLATE = """
// load %s data from csv file
int %s::Load(const char* filepath)
{
    vector<%s>* dataptr = new vector<%s>;
    std::string content = AutogenConfigManager::reader(filepath);
    CSVReader reader(CSV_SEP, CSV_QUOTE);
    reader.Parse(content);
    auto rows = reader.GetRows();
    ASSERT(!rows.empty());
    for (size_t i = 0; i < rows.size(); i++)
    {
        auto row = rows[i];
        if (!row.empty())
        {
            if (!row.empty())
            {
                %s item;
                %s::ParseFromRow(row, &item);
                dataptr->push_back(item);
            }
        }
    }
    delete %s;
    %s = dataptr;
    return 0;
}
"""

CPP_CSV_TOKEN_TEMPLATE = """
#ifndef CSV_SEP
#define CSV_SEP     ('%s')
#endif 

#ifndef CSV_QUOTE
#define CSV_QUOTE   ('%s')
#endif CSV_QUOTE
"""
