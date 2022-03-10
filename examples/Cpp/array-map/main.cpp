#include <stdio.h>
#include <assert.h>
#include <iostream>
#include <fstream>
#include <type_traits>
#include "AutogenConfig.h"
#include <absl/strings/str_format.h>
#include "common/Utils.h"

using namespace std;

#ifndef ASSERT
#define ASSERT assert
#endif

static std::string resPath = "res";


static void LoadConfig(vector<config::NewbieGuideDefine>& data) 
{
    std::string filename = absl::StrFormat("%s/%s", resPath.c_str(), "newbie_guide_define.csv");
    std::ifstream infile(filename.c_str());
    std::string line;
    while (std::getline(infile, line)) {
        auto row = parseLineToRows(line);
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
