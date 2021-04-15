#include <stdio.h>
#include <type_traits>
#include <iostream>
#include <fstream>
#include "AutoGenConfig.h"
#include "Utility/StringUtil.h"
#include "Utility/CSVReader.h"


using namespace std;
using namespace config;

static std::string resPath = "../res";

static std::string readfile(const char* filepath)
{
    std::string filename = stringPrintf("%s/%s", resPath.c_str(), filepath);
    std::ifstream ifs(filename.c_str());
    std::string content((std::istreambuf_iterator<char>(ifs)),
        (std::istreambuf_iterator<char>()));
    return std::move(content);
}

static void printGlobalProperty(const GlobalPropertyDefine& inst)
{
    cout << "GoldExchangeTimeFactor1: " << inst.GoldExchangeTimeFactor1 << endl
        << "GoldExchangeTimeFactor2: " << inst.GoldExchangeTimeFactor2 << endl
        << "GoldExchangeTimeFactor3: " << inst.GoldExchangeTimeFactor3 << endl
        << "GoldExchangeResource1Price: " << inst.GoldExchangeResource1Price << endl
        << "GoldExchangeResource1Price: " << inst.GoldExchangeResource1Price << endl
        << "GoldExchangeResource2Price: " << inst.GoldExchangeResource2Price << endl
        << "GoldExchangeResource3Price: " << inst.GoldExchangeResource3Price << endl
        << "GoldExchangeResource4Price: " << inst.GoldExchangeResource4Price << endl
        << "FreeCompleteSeconds: " << inst.FreeCompleteSeconds << endl
        << "CancelBuildReturnPercent: " << inst.CancelBuildReturnPercent << endl;

    cout << "SpawnLevelLimit: [";
    for (auto v : inst.SpawnLevelLimit) 
    {
        cout << v << ",";
    }
    cout << "]\n";

    cout << "FirstRechargeReward: {";
    for (auto v : inst.FirstRechargeReward)
    {
        cout << v.first << ":" << v.second << ",";
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

    GlobalPropertyDefine inst;
    string content = readfile("global_property_define.csv");
    CSVReader reader(config::TABULAR_CSV_SEP, config::TABULAR_CSV_QUOTE);
    reader.Parse(content);
    auto rows = reader.GetRows();
    GlobalPropertyDefine::ParseFromRows(rows, &inst);

    printGlobalProperty(inst);

    return 0;
}
