#include <stdio.h>
#include <assert.h>
#include <iostream>
#include <fstream>
#include <type_traits>
#include "AutogenConfig.h"
#include "Utility/StringUtil.h"
#include "Utility/CSVReader.h"

using namespace std;

#ifndef ASSERT
#define ASSERT assert
#endif

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

static void LoadConfig(vector<config::NewbieGuideDefine>& data) 
{
    string content = readfile("newbie_guide_define.csv");
    CSVReader reader(config::TAB_CSV_SEP, config::TAB_CSV_QUOTE);
    reader.Parse(content);
    auto rows = reader.GetRows();
    ASSERT(!rows.empty());
    for (size_t i = 0; i < rows.size(); i++)
    {
        auto row = rows[i];
        if (!row.empty())
        {
            config::NewbieGuideDefine item;
            config::NewbieGuideDefine::ParseFromRow(row, &item);
            data.push_back(item);
        }
    }
}

int main(int argc, char* argv[])
{
    vector<config::NewbieGuideDefine> data;
    LoadConfig(data);
    cout << stringPrintf("%d soldier config loaded", (int)data.size());
    for (const config::NewbieGuideDefine& item : data)
    {
        cout << stringPrintf("%s %s %d", item.Name.c_str(), item.Type.c_str(), (int)item.Accomplishment.size()) << endl;
		for (auto iter = item.Goods.begin(); iter != item.Goods.end(); ++iter)
		{
			cout << stringPrintf("\t%s: %d", iter->first.c_str(), iter->second) << endl;
		}
    }
    return 0;
}
