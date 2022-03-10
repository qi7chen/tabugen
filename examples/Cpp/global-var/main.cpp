#include <stdio.h>
#include <type_traits>
#include <iostream>
#include <fstream>
#include "AutoGenConfig.h"
#include <absl/strings/str_format.h>
#include "common/Utils.h"

using namespace std;
using namespace config;

static std::string resPath = "res";

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

    
    std::string filename = absl::StrFormat("%s/%s", resPath.c_str(), "global_property_define");
    vector<std::string> lines;
    std::ifstream infile(filename.c_str());
    std::string line;
    while (std::getline(infile, line)) {
        lines.push_back(line);
    }

    vector<vector<absl::string_view>> rows;
    for (size_t i = 0; i < lines.size(); i++)
    {
        auto row = parseLineToRows(lines[i]);
        rows.push_back(row);
    }

    GlobalPropertyDefine inst;
    GlobalPropertyDefine::ParseFromRows(rows, &inst);

    printGlobalProperty(inst);

    return 0;
}
