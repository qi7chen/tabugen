// Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

#pragma once

#include <cmath>
#include <cstdlib>
#include <string>
#include <algorithm>
#include <type_traits>
#include "StringPiece.h"


#if defined(_MSC_VER) && _MSC_VER < 1800
#define strtoll  _strtoi64
#define strtoull _strtoui64
#elif defined(__DECCXX) && defined(__osf__)
// HP C++ on Tru64 does not have strtoll, but strtol is already 64-bit.
#define strtoll strtol
#define strtoull strtoul
#endif



#define FB_STRINGIZE(x)     #x

#define FOLLY_RANGE_CHECK(condition, message, src)          \
  ((condition) ? (void)0 : throw std::range_error(          \
    (std::string(FB_STRINGIZE(__FILE__) "(" FB_STRINGIZE(__LINE__) "): ") \
     + (message) + ": '" + (src) + "'").c_str()))


inline bool ascii_isupper(char c) {
  return c >= 'A' && c <= 'Z';
}

inline bool ascii_islower(char c) {
  return c >= 'a' && c <= 'z';
}

inline char ascii_toupper(char c) {
  return ascii_islower(c) ? c - ('a' - 'A') : c;
}

inline char ascii_tolower(char c) {
  return ascii_isupper(c) ? c + ('a' - 'A') : c;
}


static int memcasecmp(const char *s1, const char *s2, size_t len) {
    const unsigned char *us1 = reinterpret_cast<const unsigned char *>(s1);
    const unsigned char *us2 = reinterpret_cast<const unsigned char *>(s2);

    for (size_t i = 0; i < len; i++) {
        const int diff =
            static_cast<int>(static_cast<unsigned char>(ascii_tolower(us1[i]))) -
            static_cast<int>(static_cast<unsigned char>(ascii_tolower(us2[i])));
        if (diff != 0) return diff;
    }
    return 0;
}

inline bool CaseEqual(StringPiece s1, StringPiece s2) {
    if (s1.size() != s2.size()) return false;
    return memcasecmp(s1.data(), s2.data(), s1.size()) == 0;
}

inline bool ParseBool(StringPiece str)
{
    if (CaseEqual(str, "true") || CaseEqual(str, "t") ||
        CaseEqual(str, "yes") || CaseEqual(str, "y") ||
        CaseEqual(str, "on") || CaseEqual(str, "1")) {
        return true;
    }
    return false;
}

inline float ParseFloat(StringPiece str)
{
    errno = 0;  // errno only gets set on errors
    float value = strtof(str.data(), nullptr);
    if (errno == ERANGE || errno == EINVAL)
    {
        return 0;
    }
    return value;
}

inline double ParseDouble(StringPiece str)
{
    errno = 0;  // errno only gets set on errors
    double value = strtod(str.data(), nullptr);
    if (errno == ERANGE || errno == EINVAL)
    {
        return 0;
    }
    return value;
}


inline int64_t ParseInt64(StringPiece str)
{
    errno = 0;  // errno only gets set on errors
    int64_t value = strtoll(str.data(), nullptr, 10);
    if (errno == ERANGE || errno == EINVAL)
    {
        return 0;
    }
    return value;
}

inline uint64_t ParseUInt64(StringPiece str)
{
    errno = 0;  // errno only gets set on errors
    uint64_t value = strtoull(str.data(), nullptr, 10);
    if (errno == ERANGE || errno == EINVAL)
    {
        return 0;
    }
    return value;
}

inline int32_t ParseInt32(StringPiece str)
{
    int64_t value = ParseInt64(str);
    FOLLY_RANGE_CHECK(
        value <= std::numeric_limits<int32_t>::max(),
        "Overflow", std::to_string(value));
    return static_cast<int32_t>(value);
}

inline uint32_t ParseUInt32(StringPiece str)
{
    uint64_t value = ParseUInt64(str);
    FOLLY_RANGE_CHECK(
        value <= std::numeric_limits<uint32_t>::max(),
        "Overflow", std::to_string(value));
    return static_cast<uint32_t>(value);
}


inline int16_t ParseInt16(StringPiece str)
{
    int64_t value = ParseInt64(str);
    FOLLY_RANGE_CHECK(
        value <= std::numeric_limits<int16_t>::max(),
        "Overflow", std::to_string(value));
    return static_cast<int16_t>(value);
}

inline uint16_t ParseUInt16(StringPiece str)
{
    uint64_t value = ParseUInt64(str);
    FOLLY_RANGE_CHECK(
        value <= std::numeric_limits<uint16_t>::max(),
        "Overflow", std::to_string(value));
    return static_cast<uint16_t>(value);
}

inline uint8_t ParseUInt8(StringPiece str)
{
    int64_t value = ParseInt64(str);
    FOLLY_RANGE_CHECK(
        value <= std::numeric_limits<uint8_t>::max(),
        "Overflow", std::to_string(value));
    return static_cast<uint8_t>(value);
}

inline int8_t ParseInt8(StringPiece str)
{
    uint64_t value = ParseUInt64(str);
    FOLLY_RANGE_CHECK(
        value <= std::numeric_limits<int8_t>::max(),
        "Overflow", std::to_string(value));
    return static_cast<int8_t>(value);
}
