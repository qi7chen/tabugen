﻿// Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
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


template <typename T>
T parseField(const std::unordered_map<std::string, std::string>& fields, const std::string& name)
{
    auto iter = fields.find(name);
    if (iter != fields.end()) {
        return boost::lexical_cast<T>(iter->second);
    }
    return T();
}

template <typename T>
std::vector<T> parseArrayField(const std::unordered_map<std::string, std::string>& fields, const std::string& name)
{
    std::vector<T> result;
    auto iter = fields.find(name);
    if (iter == fields.end()) {
        return result;
    }
    std::vector<std::string> parts;
    boost::split(parts, iter->second, boost::is_any_of("|"));
    for (size_t i = 0; i < parts.size(); i++)
    {
        auto val = boost::lexical_cast<T>(parts[i]);
        result.push_back(val);
    }
    result.shrink_to_fit();
    return result;
}

template <typename K, typename V>
std::unordered_map<K, V> parseMapField(const std::unordered_map<std::string, std::string>& fields, const std::string& name)
{
    std::unordered_map<K, V> result;
    auto iter = fields.find(name);
    if (iter == fields.end()) {
        return result;
    }
    std::vector<std::string> parts;
    boost::split(parts, iter->second, boost::is_any_of("|"));
    for (size_t i = 0; i < parts.size(); i++)
    {
        std::vector<std::string> kv;
        boost::split(kv, parts[i], boost::is_any_of("="));
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
    // plus one for the closing  .
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
