#include <stdio.h>
#include <type_traits>
#include <iostream>
#include <fstream>
#include "AutogenConfig.h"
#include <absl/strings/str_format.h>
#include "common/Utils.h"

#ifndef ASSERT
#define ASSERT assert
#endif


using namespace std;
using namespace config;

static std::string resPath = "res";


static void LoadConfig(vector<config::BoxProbabilityDefine>& data) 
{
    std::string filename = absl::StrFormat("%s/%s", resPath.c_str(), "box_probability_define.csv");
    std::ifstream infile(filename.c_str());
    std::string line;
    while (std::getline(infile, line)) {
        auto row = parseLineToRows(line);
        if (!row.empty())
        {
            config::BoxProbabilityDefine item;
            config::BoxProbabilityDefine::ParseFromRow(row, &item);
            data.push_back(item);
        }
    }
}

static void printBoxProbability(const BoxProbabilityDefine& item)
{
    cout << item.ID << " " 
        << item.Total << " " 
        << item.Time << " " 
        << item.Repeat << " " 
        ;
    cout << "[ ";
    for (size_t i = 0; i < item.ProbabilityGoods.size(); i++)
    {
        const BoxProbabilityDefine::ProbabilityGoodsDefine& goods = item.ProbabilityGoods[i];
        cout << "{ " 
            << goods.GoodsID << " "
            << goods.Num << " "
            << goods.Probability << " "
            << "},";
    }
    cout << "]" << endl;
}

int main(int argc, char* argv[])
{
    if (argc > 1)
    {
        resPath = argv[1];
    }
    vector<config::BoxProbabilityDefine> data;
    LoadConfig(data);
    cout << absl::StrFormat("%d box config loaded.\n", (int)data.size());
    for (const BoxProbabilityDefine& item : data)
    {
        printBoxProbability(item);
    }
    return 0;
}
