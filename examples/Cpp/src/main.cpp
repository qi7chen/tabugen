#include <stdio.h>
#include <assert.h>
#include <string>
#include <type_traits>
#include <iostream>
#include <fstream>
#include <unordered_map>
#include "Conv.h"
#include "StringUtil.h"
#include <unordered_map>
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
typedef std::unordered_map<std::string, std::string> Record;

static int parseNextColumn(StringPiece& line, StringPiece& field, int delim, int quote)
{
    bool in_quote = false;
    size_t start = 0;
    if (line[start] == quote) {
        in_quote = true;
        start++;
    }
    size_t pos = start;
    for (; pos < line.size(); pos++) {
        if (in_quote && line[pos] == quote) {
            if (pos + 1 < line.size() && line[pos + 1] == delim) {
                field = line.substr(start, pos - start);
                line.remove_prefix(pos - start + 2);
            }
            else { // end of line
                field = line.substr(start, pos - start);
                line.remove_prefix(pos - start + 1);
            }
            return (int)pos;
        }
        if (!in_quote && line[pos] == delim) {
            field = line.substr(start, pos - start);
            line.remove_prefix(pos - start + 1);
            return (int)pos;
        }
    }
    field = line.substr(start, pos);
    return -1;
}

static std::vector<StringPiece> lineToRow(StringPiece line, int delim = ',', int quote = '"')
{
    std::vector<StringPiece> row;
    int pos = 0;
    while (!line.empty()) {
        StringPiece field;
        int n = parseNextColumn(line, field, delim, quote);
        row.push_back(field);
        if (n < 0) {
            break;
        }
    }
    return row;
}

static std::vector<StringPiece> readToLines(StringPiece content) {
    std::vector<StringPiece> lines;
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
        StringPiece line = content.substr(begin, end - begin);
        line = StripWhitespace(line);
        if (!line.empty()) {
            lines.push_back(line);
        }
    }
    return lines;
}

int ReadCsvRecord(const std::string& filename, std::vector<Record>& out)
{
    std::ifstream infile(filename.c_str());
    std::vector<StringPiece> header;
    std::string line;
    while (std::getline(infile, line)) {
        auto row = lineToRow(line);
        if (header.empty())
        {
            header = row;
        }
        Record record;
        for (size_t i = 0; i < row.size(); i++)
        {
            const std::string& key = header[i].as_string();
            record[key] = row[i].as_string();
        }
        out.push_back(record);
    }
}

static std::string resPath = "../../datasheet/res";

template <typename T>
static void LoadCsvToConfig(const char* filename, vector<T>& data)
{
    std::string filepath = stringPrintf("%s/%s", resPath.c_str(), filename);
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
    std::string filename = stringPrintf("%s/%s", resPath.c_str(), "global_property_define.csv");
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
