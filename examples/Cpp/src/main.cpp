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
#include "SoldierDefine.h"
#include "GuideDefine.h"
#include "GlobalDefine.h"
#include "BoxDefine.h"


#ifndef ASSERT
#define ASSERT assert
#endif


using namespace std;
using namespace config;

// Read csv file to key-value records
typedef unordered_map<string, string> Record;
typedef vector<string> Row;

const regex fieldsRegx(",(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))");

void parseRow(const string& line, Row& row)
{
    // Split line to tokens
    sregex_token_iterator ti(line.begin(), line.end(), fieldsRegx, -1);
    sregex_token_iterator end;
    while (ti != end)
    {
        string token = ti->str();
        ++ti;
        row.push_back(token);
    }
    if (line.back() == ',')
    {
        row.push_back(""); // last character was a separator
    }
}

static void parseRows(const string& content, vector<Row>& rows) {
    size_t pos = 0;
    // UTF8-BOM
    if (content.size() >= 3 && content[0] == '\xEF' && content[1] == '\xBB' && content[2] == '\xBF') {
        pos = 3;
    }
    while (pos < content.size()) {
        size_t begin = pos;
        while (content[pos] != '\n') {
            pos++;
        }
        size_t end = pos;
        if (end > begin && content[end - 1] == '\r') {
            end--;
        }
        pos = end + 1;
        string line = content.substr(begin, end - begin);
        boost::trim(line);
        if (!line.empty()) {
            Row row;
            parseRow(line, row);
            rows.push_back(row);
        }
    }
}

static int ReadCsvRecord(const std::string& filename, std::vector<Record>& out)
{
    std::ifstream infile(filename.c_str());
    if (!infile.good()) {
        return -1;
    }
    std::vector<std::string> header;
    std::string line;
    while (std::getline(infile, line)) {
        Row row;
        parseRow(line, row);
        if (header.empty())
        {
            for (size_t i = 0; i < row.size(); i++)
            {
                header.push_back(row[i]);
            }
            continue;
        }
        Record record;
        for (size_t i = 0; i < row.size(); i++)
        {
            const std::string& key = header[i];
            const std::string& val = row[i];
            record.emplace(key, val);
        }
        out.push_back(record);
    }
    return 0;
}

static void RecordToKVMap(const std::vector<Record>& records, Record& out)
{
    for (size_t i = 0; i < records.size(); i++)
    {
        auto record = records[i];
        out[record["Key"]] = record["Value"];
    }
}

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

static void printSoldierProperty(const config::SoldierPropertyDefine& item)
{
    cout << item.Name << " "
        << item.Level << " "
        << item.NameID << " "
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
    LoadCsvToConfig("soldier_property_define.csv", data);
    cout << stringPrintf("%d soldier config loaded.\n", (int)data.size());
    for (const SoldierPropertyDefine& item : data)
    {
        printSoldierProperty(item);
    }
}

////////////////////////////////////////////////////////////////////////////////////////


static void printNewbieGuide(const config::NewbieGuideDefine& item)
{
    cout << item.Name << " "
        << item.Type << " "
        << item.Target << " "
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
    LoadCsvToConfig("newbie_guide_define.csv", data);
    cout << stringPrintf("%d soldier config loaded.\n", (int)data.size());
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
    auto filename = stringPrintf("%s/global_property_define.csv", resPath.c_str());
    std::vector<Record> records;
    ReadCsvRecord(filename, records);
    Record kvMap;
    RecordToKVMap(records, kvMap);

    GlobalPropertyDefine inst;
    GlobalPropertyDefine::ParseFrom(kvMap, &inst);

    printGlobalProperty(inst);
}


////////////////////////////////////////////////////////////////////////////////////////


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
    LoadCsvToConfig("box_probability_define.csv", data);
    cout << stringPrintf("%d box config loaded.\n", (int)data.size());
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
