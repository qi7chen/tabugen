#include <stdio.h>
#include <type_traits>
#include <iostream>
#include <fstream>
#include "AutogenConfig.h"
#include "Utility/StringUtil.h"
#include "Utility/CSVReader.h"

#ifndef ASSERT
#define ASSERT assert
#endif


using namespace std;
using namespace config;

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

static void LoadConfig(vector<config::BoxProbabilityDefine>& data) 
{
    string content = readfile("box_probability_define.csv");
    CSVReader reader(config::TABULAR_CSV_SEP, config::TABULAR_CSV_QUOTE);
    reader.Parse(content);
    auto rows = reader.GetRows();
    ASSERT(!rows.empty());
    for (size_t i = 0; i < rows.size(); i++)
    {
        auto row = rows[i];
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
    cout << stringPrintf("%d box config loaded.\n", (int)data.size());
    for (const BoxProbabilityDefine& item : data)
    {
        printBoxProbability(item);
    }
    return 0;
}
