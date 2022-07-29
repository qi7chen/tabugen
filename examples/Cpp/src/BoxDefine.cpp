﻿// This file is auto-generated by Tabular v0.9.1, DO NOT EDIT!

#include "BoxDefine.h"
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

// parse data object from an csv row
int BoxProbabilityDefine::ParseFrom(std::unordered_map<std::string, std::string>& record, BoxProbabilityDefine* ptr)
{
    ASSERT(ptr != nullptr);
    ptr->ID = record["ID"];
    ptr->Total = to<int>(record["Total"]);
    ptr->Time = to<int>(record["Time"]);
    ptr->Repeat = to<bool>(record["Repeat"]);
    ptr->ProbabilityGoods.reserve(3);
    for (int i = 1; i <= 3; i++)
    {
        BoxProbabilityDefine::ProbabilityGoodsDefine val;
        val.GoodsID = record[to<std::string>("GoodsID", i)];
        val.Num = to<uint32_t>(record[to<std::string>("Num", i)]);
        val.Probability = to<uint32_t>(record[to<std::string>("Probability", i)]);
        ptr->ProbabilityGoods.push_back(val);
    }
    return 0;
}


} // namespace config 
