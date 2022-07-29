﻿// This file is auto-generated by Tabugen v0.9.1, DO NOT EDIT!

#pragma once

#include <stdint.h>
#include <string>
#include <vector>
#include <unordered_map>
#include <functional>


namespace config {

// 
struct GlobalPropertyDefine 
{
    double                                GoldExchangeTimeFactor1 = 0.0;     // 金币兑换时间参数1
    double                                GoldExchangeTimeFactor2 = 0.0;     // 金币兑换时间参数2
    double                                GoldExchangeTimeFactor3 = 0.0;     // 金币兑换时间参数3
    uint16_t                              GoldExchangeResource1Price = 0;    // 金币兑换资源1价格
    uint16_t                              GoldExchangeResource2Price = 0;    // 金币兑换资源2价格
    uint16_t                              GoldExchangeResource3Price = 0;    // 金币兑换资源3价格
    uint16_t                              GoldExchangeResource4Price = 0;    // 金币兑换资源4价格
    uint16_t                              FreeCompleteSeconds = 0;           // 免费立即完成时间
    uint16_t                              CancelBuildReturnPercent = 0;      // 取消建造后返还资源比例
    bool                                  EnableSearch = false;              // 开启搜索
    std::vector<int>                      SpawnLevelLimit;                   // 最大刷新个数显示
    std::unordered_map<std::string, int>  FirstRechargeReward;               // 首充奖励
    std::unordered_map<int, int>          VIPItemReward;                     // VIP奖励

    static int ParseFrom(std::unordered_map<std::string, std::string>& fields, GlobalPropertyDefine* ptr);
};

} // namespace config
