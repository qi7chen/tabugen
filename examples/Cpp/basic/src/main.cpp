#include <stdio.h>
#include <type_traits>
#include <iostream>
#include <fstream>
#include "AutogenConfig.h"
#include "Utility/StringUtil.h"

using namespace std;

static std::string readfile(const char* filepath)
{
    std::string filename = stringPrintf("../res/%s", filepath);
    std::ifstream ifs(filename.c_str());
    std::string content((std::istreambuf_iterator<char>(ifs)),
        (std::istreambuf_iterator<char>()));
    //cout << (void*)content.data() << endl;
    //cout << content << endl;
    return std::move(content);
}

int main(int argc, char* argv[])
{
    using namespace autogen;
    AutogenConfigManager::reader = readfile;
    AutogenConfigManager::LoadAll();
    const std::vector<SoldierPropertyDefine>* all = SoldierPropertyDefine::GetData();
    cout << stringPrintf("%d soldier config loaded", (int)all->size());
    for (const SoldierPropertyDefine& item : *all)
    {
        cout << stringPrintf("%s %d", item.Name.c_str(), (int)item.Level) << endl;
    }
    return 0;
}
