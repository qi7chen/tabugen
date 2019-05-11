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
    using namespace config;
    AutogenConfigManager::reader = readfile;
    AutogenConfigManager::LoadAll();
	const std::vector<BoxProbabilityDefine>* all = BoxProbabilityDefine::GetData();
    cout << stringPrintf("%d soldier config loaded", (int)all->size());
    for (const BoxProbabilityDefine& item : *all)
    {
        cout << stringPrintf("%s, %d", item.ID.c_str(), item.Total) << endl;
		for (size_t i = 0; i < item.ProbabilityGoods.size(); i++)
		{
			const BoxProbabilityDefine::ProbabilityGoodsDefine& goods = item.ProbabilityGoods[i];
			cout << stringPrintf("\t%s: %d, %d", goods.GoodsID.c_str(), goods.Num, goods.Probability) << endl;
		}
    }
    return 0;
}
