// Copyright (C) 2024-present qi7chen@github All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

#pragma once

#include <stdarg.h>
#include <assert.h>
#include <memory>
#include <vector>
#include <string>
#include <unordered_map>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>
#include "rapidcsv.h"


#define TabDelim1 ("|")
#define TabDelim2 (":")

typedef std::unordered_map<std::string, std::string> Table;

inline void stringAppendV(std::string* dst, const char* format, va_list ap) {
    // First try with a small fixed size buffer
    static const int kSpaceLength = 1024;
    char space[kSpaceLength];

    // It's possible for methods that use a va_list to invalidate
    // the data in it upon use.  The fix is to make a copy
    // of the structure before using it and use that copy instead.
    va_list backup_ap;
    va_copy(backup_ap, ap);
    int result = vsnprintf(space, kSpaceLength, format, backup_ap);
    va_end(backup_ap);

    if (result < kSpaceLength) {
        if (result >= 0) {
            // Normal case -- everything fit.
            dst->append(space, result);
            return;
        }

#ifdef _MSC_VER
        {
            // Error or MSVC running out of space.  MSVC 8.0 and higher
            // can be asked about space needed with the special idiom below:
            va_copy(backup_ap, ap);
            result = vsnprintf(nullptr, 0, format, backup_ap);
            va_end(backup_ap);
        }
#endif

        if (result < 0) {
            // Just an error.
            return;
        }
    }

    // Increase the buffer size to the size requested by vsnprintf,
    // plus one for the closing  .
    int length = result + 1;
    std::unique_ptr<char> buf(new char[length]);

    // Restore the va_list before we use it again
    va_copy(backup_ap, ap);
    result = vsnprintf(buf.get(), length, format, backup_ap);
    va_end(backup_ap);

    if (result >= 0 && result < length) {
        // It fit
        dst->append(buf.get(), result);
    }
}

inline std::string stringPrintf(const char* format, ...)
{
    va_list ap;
    va_start(ap, format);
    std::string result;
    stringAppendV(&result, format, ap);
    va_end(ap);
    return result;
}


template <typename T>
inline T ParseField(const std::string& text)
{
    return boost::lexical_cast<T>(text);
}

template <typename T>
std::vector<T> ParseArrayField(const std::string& text)
{
    std::vector<T> result;
    std::vector<std::string> parts;
    boost::split(parts, text, boost::is_any_of(TabDelim1));
    for (size_t i = 0; i < parts.size(); i++)
    {
        auto val = boost::lexical_cast<T>(parts[i]);
        result.push_back(val);
    }
    return result;
}

template <typename K, typename V>
std::unordered_map<K, V> ParseMapField(const std::string& text)
{
    std::unordered_map<K, V> result;
    std::vector<std::string> parts;
    boost::split(parts, text, boost::is_any_of(TabDelim1));
    for (size_t i = 0; i < parts.size(); i++)
    {
        std::vector<std::string> kv;
        boost::split(kv, parts[i], boost::is_any_of(TabDelim2));
        assert(kv.size() == 2);
        if (kv.size() == 2)
        {
            auto key = boost::lexical_cast<K>(kv[0]);
            auto val = boost::lexical_cast<V>(kv[1]);
            assert(result.count(key) == 0);
            result.insert(std::make_pair(key, val));
        }
    }
    return result;
}

template <typename T>
inline T GetCellByName(const rapidcsv::Document& doc, const std::string& name, int rowIndex) {
    int colIdx = doc.GetColumnIdx(name);
    if (colIdx >= 0) {
        return doc.GetCell<T>(colIdx, rowIndex);
    }
    return T();
}

inline const std::string& GetTableField(const Table& table, const std::string& name) {
    auto iter = table.find(name);
    if (iter != table.end()) {
        return iter->second;
    }
    static std::string zero;
    return zero;
}
