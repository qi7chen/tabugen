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

#include "StringUtil.h"
#include <stdarg.h>
#include <memory>


using namespace std;

namespace detail {

inline bool is_oddspace(char c) {
    return c == '\n' || c == '\t' || c == '\r';
}

} // namespace detail

StringPiece ltrimWhitespace(StringPiece sp) {
    // Spaces other than ' ' characters are less common but should be
    // checked.  This configuration where we loop on the ' '
    // separately from oddspaces was empirically fastest.

    while (true) {
        while (!sp.empty() && sp.front() == ' ') {
            sp.pop_front();
        }
        if (!sp.empty() && detail::is_oddspace(sp.front())) {
            sp.pop_front();
            continue;
        }

        return sp;
    }
}

StringPiece rtrimWhitespace(StringPiece sp) {
    // Spaces other than ' ' characters are less common but should be
    // checked.  This configuration where we loop on the ' '
    // separately from oddspaces was empirically fastest.
    while (true) {
        while (!sp.empty() && sp.back() == ' ') {
            sp.pop_back();
        }
        if (!sp.empty() && detail::is_oddspace(sp.back())) {
            sp.pop_back();
            continue;
        }

        return sp;
    }
}

inline int stringAppendfImplHelper(char* buf,
    size_t bufsize,
    const char* format,
    va_list args)
{
    va_list args_copy;
    va_copy(args_copy, args);
    int bytes_used = vsnprintf(buf, bufsize, format, args_copy);
    va_end(args_copy);
    return bytes_used;
}

static void stringAppendfImpl(std::string& output, const char* format, va_list args)
{
    // Very simple; first, try to avoid an allocation by using an inline
    // buffer.  If that fails to hold the output string, allocate one on
    // the heap, use it instead.
    //
    // It is hard to guess the proper size of this buffer; some
    // heuristics could be based on the number of format characters, or
    // static analysis of a codebase.  Or, we can just pick a number
    // that seems big enough for simple cases (say, one line of text on
    // a terminal) without being large enough to be concerning as a
    // stack variable.
    std::array<char, 256> inline_buffer;

    int bytes_used = stringAppendfImplHelper(
        inline_buffer.data(), inline_buffer.size(), format, args);
    if (bytes_used < static_cast<int>(inline_buffer.size())) {
        if (bytes_used >= 0) {
            output.append(inline_buffer.data(), bytes_used);
            return;
        }
        // Error or MSVC running out of space.  MSVC 8.0 and higher
        // can be asked about space needed with the special idiom below:
        bytes_used = stringAppendfImplHelper(nullptr, 0, format, args);
        if (bytes_used < 0) {
            throw std::runtime_error(std::string(
                "Invalid format string; snprintf returned negative "
                "with format string: " + string(format)));
        }
    }

    // Increase the buffer size to the size requested by vsnprintf,
    // plus one for the closing \0.
    std::unique_ptr<char[]> heap_buffer(new char[bytes_used + 1]);
    int final_bytes_used =
        stringAppendfImplHelper(heap_buffer.get(), bytes_used + 1, format, args);
    // The second call can take fewer bytes if, for example, we were printing a
    // string buffer with null-terminating char using a width specifier -
    // vsnprintf("%.*s", buf.size(), buf)
    //CHECK(bytes_used >= final_bytes_used);

    // We don't keep the trailing '\0' in our output string
    output.append(heap_buffer.get(), final_bytes_used);
}

std::string stringVPrintf(const char* format, va_list ap)
{
    std::string ret;
    stringAppendfImpl(ret, format, ap);
    return ret;
}


std::string stringPrintf(const char* format, ...)
{
    va_list ap;
    va_start(ap, format);
    std::string s = stringVPrintf(format, ap);
    va_end(ap);
    return s;
}


inline bool atDelim(const char* s, StringPiece sp) {
    return !std::memcmp(s, sp.start(), sp.size());
}


template <typename OutputIter>
void splitDelimChar(StringPiece full, char c, OutputIter& result)
{
    const char* p = full.data();
    const char* end = p + full.size();
    while (p != end) {
        if (*p == c) {
            ++p;
        }
        else {
            const char* start = p;
            while (++p != end && *p != c);
            *result++ = StringPiece(start, p - start);
        }
    }
}
/*
* Shared implementation for all the split() overloads.
*
* This uses some external helpers that are overloaded to let this
* algorithm be more performant if the deliminator is a single
* character instead of a whole string.
*
* @param ignoreEmpty iff true, don't copy empty segments to output
*/
template <typename OutputIter>
void internalSplit(StringPiece full, const char* delim, OutputIter& result, bool ignoreEmpty)
{
    const size_t strSize = full.size();
    const size_t dSize = strlen(delim);
    size_t tokenStartPos = 0;
    size_t tokenSize = 0;
    const char* s = full.start();

    if (dSize > strSize || dSize == 0) {
        if (!ignoreEmpty || strSize > 0) {
            *result = full;
        }
        return;
    }

    // Optimize the common case where delim is a single character.
    if (ignoreEmpty && dSize == 1) {
        splitDelimChar(full, delim[0], result);
        return;
    }

    for (size_t i = 0; i <= strSize - dSize; ++i)
    {
        if (atDelim(&s[i], delim)) {
            if (!ignoreEmpty || tokenSize > 0) {
                *result = full.subpiece(tokenStartPos, tokenSize);
            }
            tokenStartPos = i + dSize;
            tokenSize = 0;
            i += dSize - 1;
        }
        else {
            ++tokenSize;
        }
    }
    tokenSize = strSize - tokenStartPos;
    if (!ignoreEmpty || tokenSize > 0) {
        *result = full.subpiece(tokenStartPos, tokenSize);
    }
}


// Split a string using a character delimiter. Append the components to 'result'.
//
// Note: For multi-character delimiters, this routine will split on *ANY* of
// the characters in the string, not the entire string as a single delimiter.
template <typename OutputIter>
static inline void SplitStringToIteratorUsing(StringPiece full, const char* delim, OutputIter& result)
{
    internalSplit(full, delim, result, true);
}

void SplitStringUsing(StringPiece full, const char* delim, std::vector<StringPiece>* result)
{
    std::back_insert_iterator<std::vector<StringPiece> > it(*result);
    SplitStringToIteratorUsing(full, delim, it);
}

void SplitStringAllowEmpty(StringPiece full, const char* delim, std::vector<StringPiece>* result)
{
    std::back_insert_iterator<std::vector<StringPiece> > it(*result);
    internalSplit(full, delim, it, false);
}


template <class OutputIter>
static void JoinStringsIterator(const OutputIter& start, const OutputIter& end, const char* delim, string* result)
{
    //CHECK(result != NULL);
    result->clear();
    int delim_length = strlen(delim);

    // Precompute resulting length so we can reserve() memory in one shot.
    size_t length = 0;
    for (OutputIter iter = start; iter != end; ++iter)
    {
        if (iter != start)
        {
            length += delim_length;
        }
        length += iter->size();
    }
    result->reserve(length);

    // Now combine everything.
    for (OutputIter iter = start; iter != end; ++iter)
    {
        if (iter != start)
        {
            result->append(delim, delim_length);
        }
        result->append(iter->data(), iter->size());
    }
}

void JoinStrings(const vector<StringPiece>& components,  const char* delim, string* result)
{
    JoinStringsIterator(components.begin(), components.end(), delim, result);
}
