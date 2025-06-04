#pragma once

#include "Config.h"
#include "rapidcsv.h"


typedef std::unordered_map<std::string, std::string> Table;

class DataFrame final : public config::IDataFrame {
public:
    explicit DataFrame(rapidcsv::Document& doc) : doc_(doc) {
    }

    virtual ~DataFrame()
    {
        doc_.Clear();
    }

    int GetColumnCount() const override
    {
        return (int)doc_.GetColumnCount();
    }

    bool HasColumn(const std::string& name) const override
    {
        int colIdx = doc_.GetColumnIdx(name);
        return colIdx >= 0;
    }

    std::string GetRowCell(const std::string& name, int rowIndex) const override
    {
        int colIdx = doc_.GetColumnIdx(name);
        if (colIdx >= 0) {
            return doc_.GetCell<std::string>(colIdx, rowIndex);
        }
        return "";
    }

    std::string GetKeyField(const std::string& key) const override
    {
        auto iter = table_.find(key);
        if (iter != table_.end()) {
            return iter->second;
        }
        return "";
    }

    void LoadKeyValueFields()
    {
        table_.clear();
        const auto keys = doc_.GetColumn<std::string>("Key");
        const auto values = doc_.GetColumn<std::string>("Value");
        for (size_t i = 0; i < keys.size(); i++) {
            if (i < values.size()) {
                table_[keys[i]] = values[i];
            }
        }
    }
private:
    rapidcsv::Document& doc_;
    Table table_;
};
