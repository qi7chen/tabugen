#include <stdio.h>
#include <type_traits>
#include <iostream>
#include "AutoGenConfig.h"
#include "Utility/StringUtil.h"


static std::string readfile(const char* filepath)
{
    std::string filename = stringPrintf("../%s", filepath);
    FILE* fp = fopen(filename.c_str(), "r");
    if (fp == NULL)
    {
        return "";
    }
    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    fseek(fp, 0, SEEK_SET);

    std::string content;
    content.resize(size);

    fread((char*)content.data(), 1, size, fp);
    fclose(fp);
    return std::move(content);
}

int main(int argc, char* argv[])
{
    using namespace config;
    AutogenConfigManager::reader = readfile;
    AutogenConfigManager::LoadAll();
    std::cout << "FreeCompleteSeconds: " << GlobalPropertyDefine::Instance()->FreeCompleteSeconds << std::endl;
    return 0;
}
