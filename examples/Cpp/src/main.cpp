#include <stdio.h>
#include <assert.h>
#include <type_traits>
#include <iostream>
#include <fstream>
#include <absl/strings/str_format.h>
#include "common/Utils.h"
#include "SoldierDefine.h"
#include "GuideDefine.h"
#include "GlobalDefine.h"
#include "BoxDefine.h"


#ifndef ASSERT
#define ASSERT assert
#endif


using namespace std;
using namespace config;


static std::string resPath = "res";


static void LoadSoldierConfig(vector<config::SoldierPropertyDefine>& data) 
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

static void testSoldierConfig() 
{
    vector<config::SoldierPropertyDefine> data;
    LoadSoldierConfig(data);
    cout << absl::StrFormat("%d soldier config loaded.\n", (int)data.size());
    for (const SoldierPropertyDefine& item : data)
    {
        printSoldierProperty(item);
    }
}

////////////////////////////////////////////////////////////////////////////////////////

static void LoadGuideConfig(vector<config::NewbieGuideDefine>& data) 
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

static void testNewbieGuideConfig() 
{
    vector<config::NewbieGuideDefine> data;
    LoadGuideConfig(data);
    cout << absl::StrFormat("%d soldier config loaded.\n", (int)data.size());
    for (const config::NewbieGuideDefine& item : data)
    {
        printNewbieGuide(item);
    }
}

////////////////////////////////////////////////////////////////////////////////////////

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

static void testGlobalConfig()
{
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
}


////////////////////////////////////////////////////////////////////////////////////////

static void LoadBoxConfig(vector<config::BoxProbabilityDefine>& data) 
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

static void testBoxConfig()
{
    vector<config::BoxProbabilityDefine> data;
    LoadBoxConfig(data);
    cout << absl::StrFormat("%d box config loaded.\n", (int)data.size());
    for (const BoxProbabilityDefine& item : data)
    {
        printBoxProbability(item);
    }
}

////////////////////////////////////////////////////////////////////////////////////////

int main(int argc, char* argv[])
{
    if (argc > 1)
    {
        resPath = argv[1];
    }

    testSoldierConfig();
    testNewbieGuideConfig();
    testGlobalConfig();
    testBoxConfig();

    return 0;
}