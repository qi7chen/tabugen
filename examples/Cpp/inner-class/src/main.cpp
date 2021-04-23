#include <stdio.h>
#include <type_traits>
#include <iostream>
#include <fstream>
#include "AutogenConfig.h"
#include <absl/strings/str_format.h>

#ifndef ASSERT
#define ASSERT assert
#endif


using namespace std;
using namespace config;

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

static void LoadConfig(vector<config::BoxProbabilityDefine>& data) 
{
    string content = readfile("box_probability_define.csv");
    auto lines = splitContentToLines(content);
    for (int i = 0; i < lines.size(); i++) 
    {
        auto row = parseLineToRows(lines[i], config::TABULAR_CSV_SEP, config::TABULAR_CSV_QUOTE);
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
