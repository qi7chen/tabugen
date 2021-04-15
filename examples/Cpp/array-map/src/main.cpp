#include <stdio.h>
#include <assert.h>
#include <iostream>
#include <fstream>
#include <type_traits>
#include "AutogenConfig.h"
#include "Utility/StringUtil.h"
#include "Utility/CSVReader.h"

using namespace std;

#ifndef ASSERT
#define ASSERT assert
#endif

static std::string resPath = "../res";

static std::string readfile(const char* filepath)
{
    std::string filename = stringPrintf("%s/%s", resPath.c_str(), filepath);
    std::ifstream ifs(filename.c_str());
    std::string content((std::istreambuf_iterator<char>(ifs)),
        (std::istreambuf_iterator<char>()));
    //cout << (void*)content.data() << endl;
    //cout << content << endl;
    return std::move(content);
}

static void LoadConfig(vector<config::NewbieGuideDefine>& data) 
{
    string content = readfile("newbie_guide_define.csv");
    CSVReader reader(config::TABULAR_CSV_SEP, config::TABULAR_CSV_QUOTE);
    reader.Parse(content);
    auto rows = reader.GetRows();
    ASSERT(!rows.empty());
    for (size_t i = 0; i < rows.size(); i++)
    {
        auto row = rows[i];
        if (!row.empty())
        {
            config::NewbieGuideDefine item;
            config::NewbieGuideDefine::ParseFromRow(row, &item);
            data.push_back(item);
        }
    }
}

static void printNewbieGuide(const config::NewbieGuideDefine& item) 
{
    cout << item.Name << " "
        << item.Type << " "
        << item.Target << " "
        << item.Description << " "
        ;
    cout << "{ ";
    for (auto n : item.Accomplishment)
    {
        cout << n << ", ";
    }
    cout << "} ";
        
    cout << "{ ";
    for (auto iter = item.Goods.begin(); iter != item.Goods.end(); ++iter)
    {
        cout << iter->first << ": " << iter->second << ", ";
    }
    cout << "} ";
    cout << endl;
}

int main(int argc, char* argv[])
{
    if (argc > 1)
    {
        resPath = argv[1];
    }
    vector<config::NewbieGuideDefine> data;
    LoadConfig(data);
    cout << stringPrintf("%d soldier config loaded.\n", (int)data.size());
    for (const config::NewbieGuideDefine& item : data)
    {
        printNewbieGuide(item);
    }
    return 0;
}
