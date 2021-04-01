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
#include <ctype.h>
#include <array>
#include <memory>
#include <stdexcept>
#include <iterator>
#include <algorithm>
#include <limits>
#include <random>
//#include "ScopeGuard.h"

using namespace std;

namespace {

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

void stringAppendfImpl(std::string& output, const char* format, va_list args) 
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
            throw std::runtime_error(to<std::string>(
                "Invalid format string; snprintf returned negative "
                "with format string: ",
                format));
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
    CHECK(bytes_used >= final_bytes_used);

    // We don't keep the trailing '\0' in our output string
    output.append(heap_buffer.get(), final_bytes_used);
}

} // anonymouse namespace

std::string stringPrintf(const char* format, ...) 
{
    va_list ap;
    va_start(ap, format);
    std::string s = stringVPrintf(format, ap);
    va_end(ap);
    return s;
}

std::string stringVPrintf(const char* format, va_list ap) 
{
    std::string ret;
    stringAppendfImpl(ret, format, ap);
    return ret;
}

// Basic declarations; allow for parameters of strings and string
// pieces to be specified.
std::string& stringAppendf(std::string* output, const char* format, ...) 
{
    va_list ap;
    va_start(ap, format);
    std::string& s = stringVAppendf(output, format, ap);
    va_end(ap);
    return s;
}

std::string& stringVAppendf(std::string* output,
                            const char* format,
                            va_list ap) 
{
    stringAppendfImpl(*output, format, ap);
    return *output;
}

void stringPrintf(std::string* output, const char* format, ...) 
{
    va_list ap;
    va_start(ap, format);
    stringVPrintf(output, format, ap);
    va_end(ap);
}

void stringVPrintf(std::string* output, const char* format, va_list ap) 
{
    output->clear();
    stringAppendfImpl(*output, format, ap);
};


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
    CHECK(result != NULL);
    result->clear();
    size_t delim_length = strlen(delim);

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

namespace detail {

inline bool is_oddspace(char c) {
    return c == '\n' || c == '\t' || c == '\r';
}


// Map from the character code to the hex value, or 16 if invalid hex char.
const unsigned char hexTable[] = 
{
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
   0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 16, 16, 16, 16, 16, 16, 
  16, 10, 11, 12, 13, 14, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
  16, 10, 11, 12, 13, 14, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 
};

}  // namespace detail


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

namespace {

inline void toLowerAscii8(char& c) 
{
    // Branchless tolower, based on the input-rotating trick described
    // at http://www.azillionmonkeys.com/qed/asmexample.html
    //
    // This algorithm depends on an observation: each uppercase
    // ASCII character can be converted to its lowercase equivalent
    // by adding 0x20.

    // Step 1: Clear the high order bit. We'll deal with it in Step 5.
    unsigned char rotated = c & 0x7f;
    // Currently, the value of rotated, as a function of the original c is:
    //   below 'A':   0- 64
    //   'A'-'Z':    65- 90
    //   above 'Z':  91-127

    // Step 2: Add 0x25 (37)
    rotated += 0x25;
    // Now the value of rotated, as a function of the original c is:
    //   below 'A':   37-101
    //   'A'-'Z':    102-127
    //   above 'Z':  128-164

    // Step 3: clear the high order bit
    rotated &= 0x7f;
    //   below 'A':   37-101
    //   'A'-'Z':    102-127
    //   above 'Z':    0- 36

    // Step 4: Add 0x1a (26)
    rotated += 0x1a;
    //   below 'A':   63-127
    //   'A'-'Z':    128-153
    //   above 'Z':   25- 62

    // At this point, note that only the uppercase letters have been
    // transformed into values with the high order bit set (128 and above).

    // Step 5: Shift the high order bit 2 spaces to the right: the spot
    // where the only 1 bit in 0x20 is.  But first, how we ignored the
    // high order bit of the original c in step 1?  If that bit was set,
    // we may have just gotten a false match on a value in the range
    // 128+'A' to 128+'Z'.  To correct this, need to clear the high order
    // bit of rotated if the high order bit of c is set.  Since we don't
    // care about the other bits in rotated, the easiest thing to do
    // is invert all the bits in c and bitwise-and them with rotated.
    rotated &= ~c;
    rotated >>= 2;

    // Step 6: Apply a mask to clear everything except the 0x20 bit
    // in rotated.
    rotated &= 0x20;

    // At this point, rotated is 0x20 if c is 'A'-'Z' and 0x00 otherwise

    // Step 7: Add rotated to c
    c += rotated;
}

inline void toLowerAscii32(uint32_t& c) 
{
    // Besides being branchless, the algorithm in toLowerAscii8() has another
    // interesting property: None of the addition operations will cause
    // an overflow in the 8-bit value.  So we can pack four 8-bit values
    // into a uint32_t and run each operation on all four values in parallel
    // without having to use any CPU-specific SIMD instructions.
    uint32_t rotated = c & uint32_t(0x7f7f7f7fL);
    rotated += uint32_t(0x25252525L);
    rotated &= uint32_t(0x7f7f7f7fL);
    rotated += uint32_t(0x1a1a1a1aL);

    // Step 5 involves a shift, so some bits will spill over from each
    // 8-bit value into the next.  But that's okay, because they're bits
    // that will be cleared by the mask in step 6 anyway.
    rotated &= ~c;
    rotated >>= 2;
    rotated &= uint32_t(0x20202020L);
    c += rotated;
}

inline void toLowerAscii64(uint64_t& c) 
{
    // 64-bit version of toLower32
    uint64_t rotated = c & uint64_t(0x7f7f7f7f7f7f7f7fL);
    rotated += uint64_t(0x2525252525252525L);
    rotated &= uint64_t(0x7f7f7f7f7f7f7f7fL);
    rotated += uint64_t(0x1a1a1a1a1a1a1a1aL);
    rotated &= ~c;
    rotated >>= 2;
    rotated &= uint64_t(0x2020202020202020L);
    c += rotated;
}

} // anonymouse namespace


void toLowerAscii(char* str, size_t length) 
{
    static const size_t kAlignMask64 = 7;
    static const size_t kAlignMask32 = 3;

    // Convert a character at a time until we reach an address that
    // is at least 32-bit aligned
    size_t n = (size_t)str;
    n &= kAlignMask32;
    n = std::min(n, length);
    size_t offset = 0;
    if (n != 0) {
        n = std::min(4 - n, length);
        do {
            toLowerAscii8(str[offset]);
            offset++;
        } while (offset < n);
    }

    n = (size_t)(str + offset);
    n &= kAlignMask64;
    if ((n != 0) && (offset + 4 <= length)) {
        // The next address is 32-bit aligned but not 64-bit aligned.
        // Convert the next 4 bytes in order to get to the 64-bit aligned
        // part of the input.
        toLowerAscii32(*(uint32_t*)(str + offset));
        offset += 4;
    }

    // Convert 8 characters at a time
    while (offset + 8 <= length) {
        toLowerAscii64(*(uint64_t*)(str + offset));
        offset += 8;
    }

    // Convert 4 characters at a time
    while (offset + 4 <= length) {
        toLowerAscii32(*(uint32_t*)(str + offset));
        offset += 4;
    }

    // Convert any characters remaining after the last 4-byte aligned group
    while (offset < length) {
        toLowerAscii8(str[offset]);
        offset++;
    }
}
