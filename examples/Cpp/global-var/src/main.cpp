#include <stdio.h>
#include <type_traits>
#include <iostream>
#include <fstream>
#include "AutoGenConfig.h"
#include "Utility/StringUtil.h"

using namespace std;

static std::string readfile(const char* filepath)
{
    std::string filename = stringPrintf("../res/%s", filepath);
    std::ifstream ifs(filename.c_str());
    std::string content((std::istreambuf_iterator<char>(ifs)),
        (std::istreambuf_iterator<char>()));
    return std::move(content);
}

int main(int argc, char* argv[])
{
    using namespace config;
    AutogenConfigManager::reader = readfile;
    AutogenConfigManager::LoadAll();
    auto inst = GlobalPropertyDefine::Instance();

    cout << "GoldExchangeTimeFactor1: " << inst->GoldExchangeTimeFactor1 << endl
        << "GoldExchangeTimeFactor2: " << inst->GoldExchangeTimeFactor2 << endl
        << "GoldExchangeTimeFactor3: " << inst->GoldExchangeTimeFactor3 << endl
        << "GoldExchangeResource1Price: " << inst->GoldExchangeResource1Price << endl
        << "GoldExchangeResource1Price: " << inst->GoldExchangeResource1Price << endl
        << "GoldExchangeResource2Price: " << inst->GoldExchangeResource2Price << endl
        << "GoldExchangeResource3Price: " << inst->GoldExchangeResource3Price << endl
        << "GoldExchangeResource4Price: " << inst->GoldExchangeResource4Price << endl
        << "FreeCompleteSeconds: " << inst->FreeCompleteSeconds << endl
        << "CancelBuildReturnPercent: " << inst->CancelBuildReturnPercent << endl;

    cout << "SpawnLevelLimit: ";
    for (auto v : inst->SpawnLevelLimit) 
    {
        cout << v << ",";
    }
    cout << endl;

    cout << "FirstRechargeReward: ";
    for (auto v : inst->FirstRechargeReward)
    {
        cout << v.first << ":" << v.second << ",";
    }
    cout << endl;

    return 0;
}
