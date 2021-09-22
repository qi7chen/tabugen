#include <stdio.h>
#include <assert.h>
#include <iostream>
#include <fstream>
#include <type_traits>
#include "AutogenConfig.h"
#include <absl/strings/str_format.h>

using namespace std;

#ifndef ASSERT
#define ASSERT assert
#endif

static std::string resPath = "../res";

static std::string readfile(const char* filepath)
{
    std::string filename = absl::StrFormat("%s/%s", resPath.c_str(), filepath);
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
    auto lines = splitContentToLines(content);
    for (int i = 0; i < lines.size(); i++) 
    {
        auto row = parseLineToRows(lines[i], config::TABUGEN_CSV_SEP, config::TABUGEN_CSV_QUOTE);
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
    cout << absl::StrFormat("%d soldier config loaded.\n", (int)data.size());
    for (const config::NewbieGuideDefine& item : data)
    {
        printNewbieGuide(item);
    }
    return 0;
}
