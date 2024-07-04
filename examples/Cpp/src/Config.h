﻿// This file is auto-generated by Tabugen v1.1.0, DO NOT EDIT!

#pragma once

#include <stdint.h>
#include <string>
#include <vector>
#include <unordered_map>
#include <functional>
#include "rapidcsv.h"


namespace config {

using std::vector;
using std::string;
using std::unordered_map;
using rapidcsv::Document;

// GlobalDefine,  Created from GlobalDefine.xlsx
struct GlobalDefine {
    float                          GoldExchangeTimeFactor1;      	// 金币兑换时间参数1
    float                          GoldExchangeTimeFactor2;      	// 金币兑换时间参数2
    float                          GoldExchangeTimeFactor3;      	// 金币兑换时间参数3
    int                            GoldExchangeResource1Price;   	// 金币兑换资源1价格
    int                            GoldExchangeResource2Price;   	// 金币兑换资源2价格
    int                            GoldExchangeResource3Price;   	// 金币兑换资源3价格
    int                            GoldExchangeResource4Price;   	// 金币兑换资源4价格
    int                            FreeCompleteSeconds;          	// 免费立即完成时间
    int                            CancelBuildReturnPercent;     	// 取消建造后返还资源比例
    bool                           EnableSearch;                 	// 开启搜索
    vector<int>                    SpawnLevelLimit;              	// 最大刷新个数显示
    unordered_map<string, int>     FirstRechargeReward;          	// 首充奖励
    unordered_map<int, int>        VIPItemReward;                	// VIP奖励

    static int ParseFrom(const unordered_map<string,string>& table, GlobalDefine* ptr);
};

// ItemBoxDefine,  Created from ItemBox.xlsx
struct ItemBoxDefine 
{
    string           ID;                  // 唯一ID
    int32_t          Total = 0;           // 全部数量
    int32_t          Time = 0;            // 次数
    string           Repeat;              // 可重复抽取
    vector<string>      GoodsIDs;        // 道具ID
    vector<int64_t>     Nums;            // 道具数量
    vector<int32_t>     Probabilitys;    // 抽取概率

    static int ParseRow(const Document& doc, int rowIndex, ItemBoxDefine* ptr);
};

// NewbieGuide,  Created from NewbieGuide.xlsx
struct NewbieGuide 
{
    string                      Name;                  // 名称
    string                      Desc;                  // 描述
    int32_t                     Category = 0;          // 分类
    string                      Target;                // 引导目标
    vector<int>                 Accomplishment;        // 需要完成任务
    unordered_map<string, int>  RewardGoods;           // 任务奖励

    static int ParseRow(const Document& doc, int rowIndex, NewbieGuide* ptr);
};

// SoldierDefine,  Created from Soldier.xlsx
struct SoldierDefine 
{
    int32_t  ID = 0;               // 唯一ID
    string   Name;                 // 兵种名称
    int32_t  Level = 0;            // 等级
    string   BuildingName;         // 需要建筑
    int32_t  BuildingLevel = 0;    // 建筑等级
    int32_t  RequireSpace = 0;     // 所占空间
    int32_t  Volume = 0;           // 体积
    int32_t  UpgradeTime = 0;      // 升级时间
    string   UpgradeRes;           // 升级消耗
    int32_t  UpgradeCost = 0;      // 资源消耗数量
    string   ConsumeRes;           // 训练消耗
    int32_t  ConsumeCost = 0;      // 训练消耗数量
    int32_t  ConsumeTime = 0;      // 训练时间
    int32_t  Act = 0;              // 动作
    int32_t  Hp = 0;               // 血量
    string   BombLoad;             // 装弹量
    double   AtkFrequency = 0.0;   // 攻击频率
    double   AtkRange = 0.0;       // 攻击距离
    double   MovingSpeed = 0.0;    // 移动速度
    string   EnableBurn;           // 开启燃烧

    static int ParseRow(const Document& doc, int rowIndex, SoldierDefine* ptr);
};

} // namespace config
