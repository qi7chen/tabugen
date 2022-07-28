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
#include "Range.h"

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
 * stringPrintf is much like printf but deposits its result into a
 * string. Two signatures are supported: the first simply returns the
 * resulting string, and the second appends the produced characters to
 * the specified string and returns a reference to it.
 */
std::string stringPrintf(const char* format, ...);

/* Similar to stringPrintf, with different signature. */
void stringPrintf(std::string* out, const char* fmt, ...);

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
inline std::vector<StringPiece> SplitString(StringPiece full, const char* delim, bool skip_empty = false)
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
