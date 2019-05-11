// This file is auto-generated by taxi v1.2.0, DO NOT EDIT!

#include "AutoGenConfig.h"
#include <stddef.h>
#include <assert.h>
#include <memory>
#include <fstream>
#include "Utility/Conv.h"
#include "Utility/StringUtil.h"

using namespace std;

#ifndef ASSERT
#define ASSERT assert
#endif


// parse value from text
template <typename T>
inline T ParseValue(StringPiece text)
{
    text = trimWhitespace(text);
    if (text.empty())
    {
        return T();
    }
    return to<T>(text);
}


namespace config
{

std::function<std::string(const char*)> AutogenConfigManager::reader = AutogenConfigManager::ReadFileContent;

namespace 
{
    static GlobalPropertyDefine* _instance_globalpropertydefine = nullptr;
}

void AutogenConfigManager::LoadAll()
{
    ASSERT(reader);
    GlobalPropertyDefine::Load("global_property_define.csv");
}

void AutogenConfigManager::ClearAll()
{
    delete _instance_globalpropertydefine;
    _instance_globalpropertydefine = nullptr;
}

//Load content of an asset file
std::string AutogenConfigManager::ReadFileContent(const char* filepath)
{
    ASSERT(filepath != nullptr);
    std::ifstream ifs(filepath);
    ASSERT(!ifs.fail());
    std::string content;
    content.assign(std::istreambuf_iterator<char>(ifs), std::istreambuf_iterator<char>());
    return std::move(content);
}


const GlobalPropertyDefine* GlobalPropertyDefine::Instance()
{
    ASSERT(_instance_globalpropertydefine != nullptr);
    return _instance_globalpropertydefine;
}

// load data from csv file
int GlobalPropertyDefine::Load(const char* filepath)
{
    string content = AutogenConfigManager::reader(filepath);
    MutableStringPiece sp((char*)content.data(), content.size());
    sp.replaceAll("\r\n", " \n");
    vector<vector<StringPiece>> rows;
    auto lines = Split(sp, "\n");
    ASSERT(!lines.empty());
    for (size_t i = 0; i < lines.size(); i++)
    {
        if (!lines[i].empty())
        {
            const auto& row = Split(lines[i], ",");
            if (!row.empty())
            {
                rows.push_back(row);
            }
        }
    }
    GlobalPropertyDefine* dataptr = new GlobalPropertyDefine();
    GlobalPropertyDefine::ParseFromRows(rows, dataptr);
    delete _instance_globalpropertydefine;
    _instance_globalpropertydefine = dataptr;
    return 0;
}

// parse data object from csv rows
int GlobalPropertyDefine::ParseFromRows(const vector<vector<StringPiece>>& rows, GlobalPropertyDefine* ptr)
{
    ASSERT(rows.size() >= 11 && rows[0].size() >= 3);
    ASSERT(ptr != nullptr);
    ptr->GoldExchangeTimeFactor1 = ParseValue<float>(rows[0][3]);
    ptr->GoldExchangeTimeFactor2 = ParseValue<float>(rows[1][3]);
    ptr->GoldExchangeTimeFactor3 = ParseValue<float>(rows[2][3]);
    ptr->GoldExchangeResource1Price = ParseValue<uint32_t>(rows[3][3]);
    ptr->GoldExchangeResource2Price = ParseValue<uint32_t>(rows[4][3]);
    ptr->GoldExchangeResource3Price = ParseValue<uint32_t>(rows[5][3]);
    ptr->GoldExchangeResource4Price = ParseValue<uint32_t>(rows[6][3]);
    ptr->FreeCompleteSeconds = ParseValue<uint32_t>(rows[7][3]);
    ptr->CancelBuildReturnPercent = ParseValue<uint32_t>(rows[8][3]);
    {
        const auto& array = Split(rows[9][3], "|", true);
        for (size_t i = 0; i < array.size(); i++)
        {
            ptr->SpawnLevelLimit.push_back(ParseValue<int>(array[i]));
        }
    }
    {
        const auto& mapitems = Split(rows[10][3], "|", true);
        for (size_t i = 0; i < mapitems.size(); i++)
        {
            const auto& kv = Split(mapitems[i], "=", true);
            ASSERT(kv.size() == 2);
            if(kv.size() == 2)
            {
                const auto& key = ParseValue<std::string>(kv[0]);
                ASSERT(ptr->FirstRechargeReward.count(key) == 0);
                ptr->FirstRechargeReward[key] = ParseValue<int>(kv[1]);
            }
        }
    }
    return 0;
}


} // namespace config 