#include <stdio.h>
#include <assert.h>
#include <string>
#include <regex>
#include <type_traits>
#include <iostream>
#include <fstream>
#include <unordered_map>
#include <boost/algorithm/string.hpp>
#include "Conv.h"
#include "Config.h"



#ifndef ASSERT
#define ASSERT assert
#endif


using namespace std;
using namespace rapidcsv;
using namespace config;


static std::string resPath = "../../datasheet/res";

template <typename T>
static void LoadCsvToConfig(const char* filename, vector<T>& data)
{
    auto filepath = stringPrintf("%s/%s", resPath.c_str(), filename);
    std::vector<Record> records;
    ReadCsvRecord(filepath, records);
    for (size_t i = 0; i < records.size(); i++)
    {
        T val;
        T::ParseFrom(records[i], &val);
        data.push_back(val);
    }
}

static void printSoldierProperty(const config::SoldierDefine& item)
{
    cout << item.Name << " "
        << item.Level << " "
        << item.BuildingName << " "
        << item.BuildingLevel << " "
        << item.RequireSpace << " "
        << item.UpgradeTime << " "
        << item.UpgradeCost << " "
        << item.UpgradeRes << " "
        << item.ConsumeTime << " "
        << item.Act << " "
        << item.Hp << " "
        << item.BombLoad << " "
        << item.AtkFrequency << " "
        << item.AtkRange << " "
        << item.MovingSpeed << " "
        << item.EnableBurn << " "
        << endl;
}

static void testSoldierConfig()
{
    auto filepath = stringPrintf("%s/%s", resPath.c_str(), "soldier_property_define");
    Document doc(filepath);
    for (size_t row = 0; row < doc.GetRowCount(); row++) {
        config::SoldierDefine item;
        SoldierDefine::ParseRow(doc, int(row), &item);
        printSoldierProperty(item);
    }
}


////////////////////////////////////////////////////////////////////////////////////////


static void printNewbieGuide(const config::NewbieGuide& item)
{
    cout << item.Name << " "
        << item.Category << " "
        << item.Target << " "
        ;
    cout << "{ ";
    for (auto n : item.Accomplishment)
    {
        cout << n << ", ";
    }
    cout << "} ";

    cout << "{ ";
    for (auto iter = item.RewardGoods.begin(); iter != item.RewardGoods.end(); ++iter)
    {
        cout << iter->first << ": " << iter->second << ", ";
    }
    cout << "} ";
    cout << endl;
}

static void testNewbieGuideConfig()
{
    auto filepath = stringPrintf("%s/%s", resPath.c_str(), "newbie_guide.csv");
    Document doc(filepath);
    for (size_t row = 0; row < doc.GetRowCount(); row++) {
        config::NewbieGuide item;
        NewbieGuide::ParseRow(doc, int(row), &item);
        printNewbieGuide(item);
    }
}

////////////////////////////////////////////////////////////////////////////////////////

static void printGlobalProperty(const GlobalDefine& inst)
{
    cout << "GoldExchangeTimeFactor1: " << inst.GoldExchangeTimeFactor1 << endl
        << "GoldExchangeTimeFactor2: " << inst.GoldExchangeTimeFactor2 << endl
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
    auto filepath = stringPrintf("%s/%s", resPath.c_str(), "global_define.csv");
    Document doc(filepath);
    auto keys = doc.GetColumn<string>("Key");
    auto values = doc.GetColumn<string>("Value");
    unordered_map<string, string> table;
    for (size_t i = 0; i < keys.size(); i++) {
        if (i < values.size()) {
            table[keys[i]] = values[i];
        }
    }
    for (size_t row = 0; row < doc.GetRowCount(); row++) {
        config::NewbieGuide item;
        NewbieGuide::ParseRow(doc, int(row), &item);
        printNewbieGuide(item);
    }

    GlobalDefine inst;
    GlobalDefine::ParseFrom(table, &inst);

    printGlobalProperty(inst);
}


////////////////////////////////////////////////////////////////////////////////////////


static void printBoxProbability(const ItemBoxDefine& item)
{
    cout << item.ID << " "
        << item.Total << " "
        << item.Time << " "
        << item.Repeat << " "
        ;
    cout << "[ ";
    for (size_t i = 0; i < item.GoodsIDs.size(); i++)
    {
        cout << "{ "
            << item.GoodsIDs[i] << " "
            << item.Nums[i] << " "
            << item.Probabilitys[i] << " "
            << "},";
    }
    cout << "]" << endl;
}

static void testBoxConfig()
{
    auto filepath = stringPrintf("%s/%s", resPath.c_str(), "item_box_define.csv");
    Document doc(filepath);
    for (size_t row = 0; row < doc.GetRowCount(); row++) {
        config::ItemBoxDefine item;
        ItemBoxDefine::ParseRow(doc, int(row), &item);
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
