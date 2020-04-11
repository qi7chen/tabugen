#include <stdio.h>
#include <type_traits>
#include <iostream>
#include <fstream>
#include "AutoGenConfig.h"
#include "Utility/StringUtil.h"


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
    std::cout << "FreeCompleteSeconds: " << GlobalPropertyDefine::Instance()->FreeCompleteSeconds << std::endl;
    return 0;
}
