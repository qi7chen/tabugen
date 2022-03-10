#include <stdio.h>
#include <assert.h>
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


static void LoadConfig(vector<config::SoldierPropertyDefine>& data) 
{
    std::string filename = absl::StrFormat("%s/%s", resPath.c_str(), "soldier_property_define.csv");
    std::ifstream infile(filename.c_str());
    std::string line;
    while (std::getline(infile, line)) {
        auto row = parseLineToRows(line);
        if (!row.empty())
        {
            config::SoldierPropertyDefine item;
            config::SoldierPropertyDefine::ParseFromRow(row, &item);
            data.push_back(item);
        }
    }
}

static void printSoldierProperty(const config::SoldierPropertyDefine& item) 
{
    cout << item.Name << " "
        << item.Level << " "
        << item.NameID << " "
        << item.Description << " "
        << item.BuildingName << " "
        << item.BuildingLevel << " "
        << item.RequireSpace << " "
        << item.UpgradeTime << " "
        << item.UpgradeMaterialID << " "
        << item.UpgradeMaterialNum << " "
        << item.ConsumeMaterial << " "
        << item.ConsumeMaterialNum << " "
        << item.ConsumeTime << " "
        << item.Act << " "
        << item.Hp << " "
        << item.BombLoad << " "
        << item.Duration << " "
        << item.TriggerInterval << " "
        << item.SearchScope << " "
        << item.AtkFrequency << " "
        << item.AtkRange << " "
        << item.MovingSpeed << " "
        << item.EnableBurn << " "
        << endl;
}

int main(int argc, char* argv[])
{
    if (argc > 1)
    {
        resPath = argv[1];
    }
    vector<config::SoldierPropertyDefine> data;
    LoadConfig(data);
    cout << absl::StrFormat("%d soldier config loaded.\n", (int)data.size());
    for (const SoldierPropertyDefine& item : data)
    {
        printSoldierProperty(item);
    }
    return 0;
}
