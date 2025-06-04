// Copyright (C) 2024-present qi7chen@github All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

#include <stdio.h>
#include <assert.h>
#include <string>
#include <regex>
#include <iostream>
#include <unordered_map>
#include <fmt/format.h>

#include "dataframe.h"

#ifndef ASSERT
#define ASSERT assert
#endif


using namespace std;
using namespace config;


static std::string resPath = "../../datasheet/res";

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
    auto filepath = fmt::format("{}/soldier_define.csv", resPath);
    rapidcsv::Document doc(filepath);
    DataFrame table(doc);
    for (size_t row = 0; row < doc.GetRowCount(); row++) {
        config::SoldierDefine item;
        SoldierDefine::ParseRow(&table, int(row), &item);
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
    auto filepath = fmt::format("{}/newbie_guide.csv", resPath);
    rapidcsv::Document doc(filepath);
    DataFrame table(doc);
    for (size_t row = 0; row < doc.GetRowCount(); row++) {
        config::NewbieGuide item;
        NewbieGuide::ParseRow(&table, int(row), &item);
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
    auto filepath = fmt::format("{}/global_define.csv", resPath);
    rapidcsv::Document doc(filepath);
    DataFrame table(doc);
    table.LoadKeyValueFields();
    GlobalDefine inst;
    GlobalDefine::ParseFrom(&table, &inst);

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
    auto filepath = fmt::format("{}/item_box_define.csv", resPath);
    rapidcsv::Document doc(filepath);
    DataFrame table(doc);
    for (size_t row = 0; row < doc.GetRowCount(); row++) {
        config::ItemBoxDefine item;
        ItemBoxDefine::ParseRow(&table, int(row), &item);
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

    try {
        testSoldierConfig();
        testNewbieGuideConfig();
        testGlobalConfig();
        testBoxConfig();
    }
    catch (std::exception& e) {
        cout << e.what() << endl;
    }

    return 0;
}
