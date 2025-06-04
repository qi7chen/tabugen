#pragma once

#include <cassert>
#include <string>
#include <charconv>
#include <type_traits>
#include <absl/strings/str_split.h>


template <class Tgt>
typename std::enable_if<
    std::is_same<typename std::remove_cv<Tgt>::type, bool>::value,
Tgt>::type
parseTo(const std::string_view& text)
{
    switch (text.size())
    {
        case 0:
            return false;
        case 1:
            return text == "1"  || text == "y" || text == "Y" || text == "t" || text == "T" ;
        case 2:
            return text == "on" || text == "On" || text == "ON";
        case 3:
            return text == "yes" || text == "Yes" || text == "YES";
    }
    return false;
}

template <class Tgt>
typename std::enable_if<
    std::is_same<typename std::remove_cv<Tgt>::type, std::string>::value,
Tgt>::type
parseTo(const std::string_view& text)
{
    return std::string(text.data(), text.length());
}

template <class Tgt>
typename std::enable_if<
    std::is_integral<Tgt>::value && !std::is_same<typename std::remove_cv<Tgt>::type, bool>::value,
Tgt>::type
parseTo(const std::string_view& text)
{
    Tgt result;
    std::from_chars(text.data(), text.data()+text.size(), result, 10);
    return std::move(result);
}

template <class Tgt>
typename std::enable_if<
    std::is_floating_point<Tgt>::value, Tgt>::type
parseTo(const std::string_view& text)
{
    Tgt result;
    std::from_chars(text.data(), text.data()+text.size(), result, std::chars_format::general);
    return std::move(result);
}


template <typename T>
std::vector<T> parseArray(const std::string& text, const char* delim)
{
    std::vector<T> result;
    std::vector<std::string> parts = absl::StrSplit(text, delim);
    for (size_t i = 0; i < parts.size(); i++)
    {
        auto val = parseTo<T>(parts[i]);
        result.push_back(val);
    }
    return result; // C42679
}

template <typename K, typename V>
std::unordered_map<K, V> parseMap(const std::string& text, const char* delim1, const char* delim2)
{
    std::unordered_map<K, V> result;
    std::vector<std::string> parts = absl::StrSplit(text, delim1);
    for (size_t i = 0; i < parts.size(); i++)
    {
        std::vector<std::string> kv = absl::StrSplit(parts[i], delim2);
        assert(kv.size() == 2);
        if (kv.size() == 2)
        {
            auto key = parseTo<K>(kv[0]);
            auto val = parseTo<V>(kv[1]);
            assert(result.count(key) == 0);
            result.insert(std::make_pair(key, val));
        }
    }
    return result; // C42679
}
