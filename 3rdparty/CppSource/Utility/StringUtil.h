/*
 * Copyright 2015 Facebook, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
 
#pragma once

#include <string>
#include <vector>
#include <type_traits>
#include "Range.h"
#include "Conv.h"


/**
 * stringPrintf is much like printf but deposits its result into a
 * string. Two signatures are supported: the first simply returns the
 * resulting string, and the second appends the produced characters to
 * the specified string and returns a reference to it.
 */
std::string stringPrintf(FOLLY_PRINTF_FORMAT const char* format, ...)
  FOLLY_PRINTF_FORMAT_ATTR(1, 2);

/* Similar to stringPrintf, with different signature. */
void stringPrintf(std::string* out, FOLLY_PRINTF_FORMAT const char* fmt, ...)
  FOLLY_PRINTF_FORMAT_ATTR(2, 3);

std::string& stringAppendf(std::string* output,
                          FOLLY_PRINTF_FORMAT const char* format, ...)
  FOLLY_PRINTF_FORMAT_ATTR(2, 3);

/**
 * Similar to stringPrintf, but accepts a va_list argument.
 *
 * As with vsnprintf() itself, the value of ap is undefined after the call.
 * These functions do not call va_end() on ap.
 */
std::string stringVPrintf(const char* format, va_list ap);
void stringVPrintf(std::string* out, const char* format, va_list ap);
std::string& stringVAppendf(std::string* out, const char* format, va_list ap);


/**
* Split a string using a character delimiter. Append the components
* to 'result'.  If there are consecutive delimiters, this function skips
* over all of them.
*/
void SplitStringUsing(StringPiece full, const char* delim, std::vector<StringPiece>* result);

/**
* Split a string using one or more byte delimiters, presented
* as a nul-terminated c string. Append the components to 'result'.
* If there are consecutive delimiters, this function will return
* corresponding empty strings.  If you want to drop the empty
* strings, try SplitStringUsing().
*
* If "full" is the empty string, yields an empty string as the only value.
*/
void SplitStringAllowEmpty(StringPiece full, const char* delim, std::vector<StringPiece>* result);

/**
* Split a string using a character delimiter.
*/
inline std::vector<StringPiece> Split(StringPiece full, const char* delim, bool skip_empty = false)
{
    std::vector<StringPiece> result;
    if (skip_empty)
    {
        SplitStringUsing(full, delim, &result);
    }
    else
    {
        SplitStringAllowEmpty(full, delim, &result);
    }
    return result;
}

/**
 * These methods concatenate a vector of strings into a C++ string, using
 * the C-string "delim" as a separator between components. There are two
 * flavors of the function, one flavor returns the concatenated string,
 * another takes a pointer to the target string. In the latter case the
 * target string is cleared and overwritten.
 */
void JoinStrings(const std::vector<StringPiece>& components, const char* delim, std::string* result);

inline std::string JoinStrings(const std::vector<StringPiece>& components, const char* delim)
{
    std::string result;
    JoinStrings(components, delim, &result);
    return result;
}


/**
 * Returns a subpiece with all whitespace removed from the front of @sp.
 * Whitespace means any of [' ', '\n', '\r', '\t'].
 */
StringPiece ltrimWhitespace(StringPiece sp);

/**
 * Returns a subpiece with all whitespace removed from the back of @sp.
 * Whitespace means any of [' ', '\n', '\r', '\t'].
 */
StringPiece rtrimWhitespace(StringPiece sp);

/**
 * Returns a subpiece with all whitespace removed from the back and front of @sp.
 * Whitespace means any of [' ', '\n', '\r', '\t'].
 */
inline StringPiece trimWhitespace(StringPiece sp) {
    return ltrimWhitespace(rtrimWhitespace(sp));
}

/**
 * Returns a subpiece with all whitespace removed from the front of @sp.
 * Whitespace means any of [' ', '\n', '\r', '\t'].
 * DEPRECATED: @see ltrimWhitespace @see rtrimWhitespace
 */
inline StringPiece skipWhitespace(StringPiece sp) {
    return ltrimWhitespace(sp);
}

inline bool IsHexDigit(int c) 
{
    return (c >= '0' && c <= '9') ||
        (c >= 'A' && c <= 'F') ||
        (c >= 'a' && c <= 'f');
}

inline bool IsLowerHexDigit(int c) 
{
    return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f');
}

inline bool IsAsciiWhitespace(int c) 
{
    return c == ' ' || c == '\r' || c == '\n' || c == '\t';
}

inline bool IsAsciiAlpha(int c) 
{
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
}

inline bool IsAsciiUpper(int c) 
{
    return c >= 'A' && c <= 'Z';
}

inline bool IsAsciiLower(int c) 
{
    return c >= 'a' && c <= 'z';
}

inline bool IsAsciiDigit(int c) 
{
    return c >= '0' && c <= '9';
}

/**
 * Returns a subpiece with all whitespace removed from the front of @sp.
 * Whitespace means any of [' ', '\n', '\r', '\t'].
 */
StringPiece skipWhitespace(StringPiece sp);

/**
 * Fast, in-place lowercasing of ASCII alphabetic characters in strings.
 * Leaves all other characters unchanged, including those with the 0x80
 * bit set.
 * @param str String to convert
 * @param len Length of str, in bytes
 */
void toLowerAscii(char* str, size_t length);

inline void toLowerAscii(MutableStringPiece str) {
  toLowerAscii(str.begin(), str.size());
}

// Fills `outlen` bytes of `output` with random data. Thread-safe.
void RandBytes(void* output, size_t outlen);


// parse value from text
template <typename T>
inline T parseTextAs(StringPiece text)
{
    text = trimWhitespace(text);
    if (text.empty())
    {
        return T();
    }
    return to<T>(text);
}
