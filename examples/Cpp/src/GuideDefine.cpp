﻿// This file is auto-generated by Tabular v0.9.1, DO NOT EDIT!

#include "GuideDefine.h"
#include <stddef.h>
#include <assert.h>
#include <memory>
#include <fstream>
#include "Conv.h"
#include "StringUtil.h"

using namespace std;

#ifndef ASSERT
#define ASSERT assert
#endif


namespace config {

// parse NewbieGuideDefine from string fields
int NewbieGuideDefine::ParseFrom(std::unordered_map<std::string, std::string>& record, NewbieGuideDefine* ptr)
{
    ASSERT(ptr != nullptr);
    ptr->Name = record["Name"];
    ptr->Type = record["Type"];
    ptr->Target = record["Target"];
    {
        auto arr = SplitString(record["Accomplishment"], "|");
        for (size_t i = 0; i < arr.size(); i++)
        {
            if (!arr[i].empty()) {
                auto val = ParseInt16(arr[i]);
                ptr->Accomplishment.emplace_back(val);
            }
        }
    }
    {
        auto kvs = SplitString(record["Goods"], "|");
        for (size_t i = 0; i < kvs.size(); i++)
        {
            auto kv = SplitString(kvs[i], "=");
            ASSERT(kv.size() == 2);
            if(kv.size() == 2)
            {
                auto key = StripWhitespace(kv[0]);
                auto val = ParseUInt32(kv[1]);
                ASSERT(ptr->Goods.count(key) == 0);
                ptr->Goods.emplace(std::make_pair(key, val));
            }
        }
    }
    ptr->Description = record["Description"];
    return 0;
}


} // namespace config 
