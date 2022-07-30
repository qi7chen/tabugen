// Protocol Buffers - Google's data interchange format
// Copyright 2008 Google Inc.  All rights reserved.
// https://developers.google.com/protocol-buffers/
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
//     * Redistributions of source code must retain the above copyright
// notice, this list of conditions and the following disclaimer.
//     * Redistributions in binary form must reproduce the above
// copyright notice, this list of conditions and the following disclaimer
// in the documentation and/or other materials provided with the
// distribution.
//     * Neither the name of Google Inc. nor the names of its
// contributors may be used to endorse or promote products derived from
// this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
// LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

// from google3/strings/strutil.cc


#include "StringUtil.h"
#include <errno.h>
#include <stdarg.h> 
#include <float.h>    // FLT_DIG and DBL_DIG
#include <limits.h>
#include <stdio.h>
#include <cmath>
#include <iterator>
#include <limits>
#include <memory>



#ifdef _WIN32
// MSVC has only _snprintf, not snprintf.
//
// MinGW has both snprintf and _snprintf, but they appear to be different
// functions.  The former is buggy.  When invoked like so:
//   char buffer[32];
//   snprintf(buffer, 32, "%.*g\n", FLT_DIG, 1.23e10f);
// it prints "1.23000e+10".  This is plainly wrong:  %g should never print
// trailing zeros after the decimal point.  For some reason this bug only
// occurs with some input values, not all.  In any case, _snprintf does the
// right thing, so we use it.
#define snprintf _snprintf
#endif


// These are defined as macros on some platforms.  #undef them so that we can
// redefine them.
#undef isxdigit
#undef isprint

// The definitions of these in ctype.h change based on locale.  Since our
// string manipulation is all in relation to the protocol buffer and C++
// languages, we always want to use the C locale.  So, we re-define these
// exactly as we want them.
inline bool isxdigit(char c) {
  return ('0' <= c && c <= '9') ||
         ('a' <= c && c <= 'f') ||
         ('A' <= c && c <= 'F');
}

inline bool isprint(char c) {
  return c >= 0x20 && c <= 0x7E;
}


void StringAppendV(std::string* dst, const char* format, va_list ap) {
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
  // plus one for the closing \0.
  int length = result+1;
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

std::string StringPrintf(const char* format, ...) {
    va_list ap;
    va_start(ap, format);
    std::string result;
    StringAppendV(&result, format, ap);
    va_end(ap);
    return result;
}

// ----------------------------------------------------------------------
// ReplaceCharacters
//    Replaces any occurrence of the character 'remove' (or the characters
//    in 'remove') with the character 'replacewith'.
// ----------------------------------------------------------------------
void ReplaceCharacters(std::string *s, const char *remove, char replacewith) {
  const char *str_start = s->c_str();
  const char *str = str_start;
  for (str = strpbrk(str, remove);
       str != nullptr;
       str = strpbrk(str + 1, remove)) {
    (*s)[str - str_start] = replacewith;
  }
}

inline bool ascii_isspace(char c) {
    return c == ' ' || c == '\t' || c == '\n' || c == '\v' || c == '\f' ||
        c == '\r';
}


std::string& StripWhitespace(std::string& str) {
  size_t str_length = str.length();

  // Strip off leading whitespace.
  size_t first = 0;
  while (first < str_length && ascii_isspace(str.at(first))) {
    ++first;
  }
  // If entire string is white space.
  if (first == str_length) {
    str.clear();
    return str;
  }
  if (first > 0) {
    str.erase(0, first);
    str_length -= first;
  }

  // Strip off trailing whitespace.
  size_t last = str_length - 1;
  while (last >= 0 && ascii_isspace(str.at(last))) {
    --last;
  }
  if (last != (str_length - 1) && last >= 0) {
    str.erase(last + 1, std::string::npos);
  }
  return str;
}

StringPiece StripWhitespace(StringPiece s)
{
    // trim left
    while (true) {
        while (!s.empty() && s[0] == ' ') {
            s.remove_prefix(1);
        }
        if (!s.empty() && ascii_isspace(s[0])) {
            s.remove_prefix(1);
            continue;
        }
        break;
    }
    // trim right
    while (true) {
        while (!s.empty() && s[0] == ' ') {
            s.remove_suffix(1);
        }
        if (!s.empty() && ascii_isspace(s[0])) {
            s.remove_suffix(1);
            continue;
        }
        break;
    }
    return s;
}



// ----------------------------------------------------------------------
// StringReplace()
//    Replace the "old" pattern with the "new" pattern in a string,
//    and append the result to "res".  If replace_all is false,
//    it only replaces the first instance of "old."
// ----------------------------------------------------------------------

void StringReplace(const std::string &s, const std::string &oldsub,
                   const std::string &newsub, bool replace_all,
                   std::string *res) {
  if (oldsub.empty()) {
    res->append(s);  // if empty, append the given string.
    return;
  }

  std::string::size_type start_pos = 0;
  std::string::size_type pos;
  do {
    pos = s.find(oldsub, start_pos);
    if (pos == std::string::npos) {
      break;
    }
    res->append(s, start_pos, pos - start_pos);
    res->append(newsub);
    start_pos = pos + oldsub.size();  // start searching again after the "old"
  } while (replace_all);
  res->append(s, start_pos, s.length() - start_pos);
}

// ----------------------------------------------------------------------
// StringReplace()
//    Give me a string and two patterns "old" and "new", and I replace
//    the first instance of "old" in the string with "new", if it
//    exists.  If "global" is true; call this repeatedly until it
//    fails.  RETURN a new string, regardless of whether the replacement
//    happened or not.
// ----------------------------------------------------------------------

std::string StringReplace(const std::string &s, const std::string &oldsub,
                          const std::string &newsub, bool replace_all) {
  std::string ret;
  StringReplace(s, oldsub, newsub, replace_all, &ret);
  return ret;
}

// ----------------------------------------------------------------------
// SplitStringUsing()
//    Split a string using a character delimiter. Append the components
//    to 'result'.
//
// Note: For multi-character delimiters, this routine will split on *ANY* of
// the characters in the string, not the entire string as a single delimiter.
// ----------------------------------------------------------------------
template <typename ITR>
static inline void SplitStringToIteratorUsing(StringPiece full,
                                              const char *delim, ITR &result) {
  // Optimize the common case where delim is a single character.
  if (delim[0] != '\0' && delim[1] == '\0') {
    char c = delim[0];
    const char* p = full.data();
    const char* end = p + full.size();
    while (p != end) {
      if (*p == c) {
        ++p;
      } else {
        const char* start = p;
        while (++p != end && *p != c);
        *result++ = std::string(start, p - start);
      }
    }
    return;
  }

  std::string::size_type begin_index, end_index;
  begin_index = full.find_first_not_of(delim);
  while (begin_index != std::string::npos) {
    end_index = full.find_first_of(delim, begin_index);
    if (end_index == std::string::npos) {
      *result++ = std::string(full.substr(begin_index));
      return;
    }
    *result++ =
        std::string(full.substr(begin_index, (end_index - begin_index)));
    begin_index = full.find_first_not_of(delim, end_index);
  }
}

void SplitStringUsing(StringPiece full, const char *delim,
                      std::vector<std::string> *result) {
  std::back_insert_iterator<std::vector<std::string> > it(*result);
  SplitStringToIteratorUsing(full, delim, it);
}

// Split a string using a character delimiter. Append the components
// to 'result'.  If there are consecutive delimiters, this function
// will return corresponding empty strings. The string is split into
// at most the specified number of pieces greedily. This means that the
// last piece may possibly be split further. To split into as many pieces
// as possible, specify 0 as the number of pieces.
//
// If "full" is the empty string, yields an empty string as the only value.
//
// If "pieces" is negative for some reason, it returns the whole string
// ----------------------------------------------------------------------
template <typename ITR>
static inline void SplitStringToIteratorAllowEmpty(StringPiece full,
                                                   const char *delim,
                                                   int pieces, ITR &result) {
  std::string::size_type begin_index, end_index;
  begin_index = 0;

  for (int i = 0; (i < pieces-1) || (pieces == 0); i++) {
    end_index = full.find_first_of(delim, begin_index);
    if (end_index == std::string::npos) {
      *result++ = std::string(full.substr(begin_index));
      return;
    }
    *result++ =
        std::string(full.substr(begin_index, (end_index - begin_index)));
    begin_index = end_index + 1;
  }
  *result++ = std::string(full.substr(begin_index));
}

void SplitStringAllowEmpty(StringPiece full, const char *delim,
                           std::vector<std::string> *result) {
  std::back_insert_iterator<std::vector<std::string> > it(*result);
  SplitStringToIteratorAllowEmpty(full, delim, 0, it);
}

// ----------------------------------------------------------------------
// JoinStrings()
//    This merges a vector of string components with delim inserted
//    as separaters between components.
//
// ----------------------------------------------------------------------
template <class ITERATOR>
static void JoinStringsIterator(const ITERATOR &start, const ITERATOR &end,
                                const char *delim, std::string *result) {
  // GOOGLE_CHECK(result != nullptr);
  result->clear();
  size_t delim_length = strlen(delim);

  // Precompute resulting length so we can reserve() memory in one shot.
  size_t length = 0;
  for (ITERATOR iter = start; iter != end; ++iter) {
    if (iter != start) {
      length += delim_length;
    }
    length += iter->size();
  }
  result->reserve(length);

  // Now combine everything.
  for (ITERATOR iter = start; iter != end; ++iter) {
    if (iter != start) {
      result->append(delim, delim_length);
    }
    result->append(iter->data(), iter->size());
  }
}

void JoinStrings(const std::vector<std::string> &components, const char *delim,
                 std::string *result) {
  JoinStringsIterator(components.begin(), components.end(), delim, result);
}

// ----------------------------------------------------------------------
// UnescapeCEscapeSequences()
//    This does all the unescaping that C does: \ooo, \r, \n, etc
//    Returns length of resulting string.
//    The implementation of \x parses any positive number of hex digits,
//    but it is an error if the value requires more than 8 bits, and the
//    result is truncated to 8 bits.
//
//    The second call stores its errors in a supplied string vector.
//    If the string vector pointer is nullptr, it reports the errors with LOG().
// ----------------------------------------------------------------------

#define IS_OCTAL_DIGIT(c) (((c) >= '0') && ((c) <= '7'))

// Protocol buffers doesn't ever care about errors, but I don't want to remove
// the code.
#define LOG_STRING(LEVEL, VECTOR) GOOGLE_LOG_IF(LEVEL, false)


// ----------------------------------------------------------------------
// strto32_adaptor()
// strtou32_adaptor()
//    Implementation of strto[u]l replacements that have identical
//    overflow and underflow characteristics for both ILP-32 and LP-64
//    platforms, including errno preservation in error-free calls.
// ----------------------------------------------------------------------

int32_t strto32_adaptor(const char *nptr, char **endptr, int base) {
  const int saved_errno = errno;
  errno = 0;
  const long result = strtol(nptr, endptr, base);
  if (errno == ERANGE && result == LONG_MIN) {
    return std::numeric_limits<int32_t>::min();
  } else if (errno == ERANGE && result == LONG_MAX) {
    return std::numeric_limits<int32_t>::max();
  } else if (errno == 0 && result < std::numeric_limits<int32_t>::min()) {
    errno = ERANGE;
    return std::numeric_limits<int32_t>::min();
  } else if (errno == 0 && result > std::numeric_limits<int32_t>::max()) {
    errno = ERANGE;
    return std::numeric_limits<int32_t>::max();
  }
  if (errno == 0)
    errno = saved_errno;
  return static_cast<int32_t>(result);
}

uint32_t strtou32_adaptor(const char *nptr, char **endptr, int base) {
  const int saved_errno = errno;
  errno = 0;
  const unsigned long result = strtoul(nptr, endptr, base);
  if (errno == ERANGE && result == ULONG_MAX) {
    return std::numeric_limits<uint32_t>::max();
  } else if (errno == 0 && result > std::numeric_limits<uint32_t>::max()) {
    errno = ERANGE;
    return std::numeric_limits<uint32_t>::max();
  }
  if (errno == 0)
    errno = saved_errno;
  return static_cast<uint32_t>(result);
}

inline bool safe_parse_sign(std::string *text /*inout*/,
                            bool *negative_ptr /*output*/) {
  const char* start = text->data();
  const char* end = start + text->size();

  // Consume whitespace.
  while (start < end && (start[0] == ' ')) {
    ++start;
  }
  while (start < end && (end[-1] == ' ')) {
    --end;
  }
  if (start >= end) {
    return false;
  }

  // Consume sign.
  *negative_ptr = (start[0] == '-');
  if (*negative_ptr || start[0] == '+') {
    ++start;
    if (start >= end) {
      return false;
    }
  }
  *text = text->substr(start - text->data(), end - start);
  return true;
}

template <typename IntType>
bool safe_parse_positive_int(std::string text, IntType *value_p) {
  int base = 10;
  IntType value = 0;
  const IntType vmax = std::numeric_limits<IntType>::max();
  assert(vmax > 0);
  assert(vmax >= base);
  const IntType vmax_over_base = vmax / base;
  const char* start = text.data();
  const char* end = start + text.size();
  // loop over digits
  for (; start < end; ++start) {
    unsigned char c = static_cast<unsigned char>(start[0]);
    int digit = c - '0';
    if (digit >= base || digit < 0) {
      *value_p = value;
      return false;
    }
    if (value > vmax_over_base) {
      *value_p = vmax;
      return false;
    }
    value *= base;
    if (value > vmax - digit) {
      *value_p = vmax;
      return false;
    }
    value += digit;
  }
  *value_p = value;
  return true;
}

template <typename IntType>
bool safe_parse_negative_int(const std::string &text, IntType *value_p) {
  int base = 10;
  IntType value = 0;
  const IntType vmin = std::numeric_limits<IntType>::min();
  assert(vmin < 0);
  assert(vmin <= 0 - base);
  IntType vmin_over_base = vmin / base;
  // 2003 c++ standard [expr.mul]
  // "... the sign of the remainder is implementation-defined."
  // Although (vmin/base)*base + vmin%base is always vmin.
  // 2011 c++ standard tightens the spec but we cannot rely on it.
  if (vmin % base > 0) {
    vmin_over_base += 1;
  }
  const char* start = text.data();
  const char* end = start + text.size();
  // loop over digits
  for (; start < end; ++start) {
    unsigned char c = static_cast<unsigned char>(start[0]);
    int digit = c - '0';
    if (digit >= base || digit < 0) {
      *value_p = value;
      return false;
    }
    if (value < vmin_over_base) {
      *value_p = vmin;
      return false;
    }
    value *= base;
    if (value < vmin + digit) {
      *value_p = vmin;
      return false;
    }
    value -= digit;
  }
  *value_p = value;
  return true;
}

template <typename IntType>
bool safe_int_internal(std::string text, IntType *value_p) {
  *value_p = 0;
  bool negative;
  if (!safe_parse_sign(&text, &negative)) {
    return false;
  }
  if (!negative) {
    return safe_parse_positive_int(text, value_p);
  } else {
    return safe_parse_negative_int(text, value_p);
  }
}

template <typename IntType>
bool safe_uint_internal(std::string text, IntType *value_p) {
  *value_p = 0;
  bool negative;
  if (!safe_parse_sign(&text, &negative) || negative) {
    return false;
  }
  return safe_parse_positive_int(text, value_p);
}

// ----------------------------------------------------------------------
// FastIntToBuffer()
// FastInt64ToBuffer()
// FastHexToBuffer()
// FastHex64ToBuffer()
// FastHex32ToBuffer()
// ----------------------------------------------------------------------

// Offset into buffer where FastInt64ToBuffer places the end of string
// null character.  Also used by FastInt64ToBufferLeft.
static const int kFastInt64ToBufferOffset = 21;

char *FastInt64ToBuffer(int64_t i, char* buffer) {
  // We could collapse the positive and negative sections, but that
  // would be slightly slower for positive numbers...
  // 22 bytes is enough to store -2**64, -18446744073709551616.
  char* p = buffer + kFastInt64ToBufferOffset;
  *p-- = '\0';
  if (i >= 0) {
    do {
      *p-- = '0' + i % 10;
      i /= 10;
    } while (i > 0);
    return p + 1;
  } else {
    // On different platforms, % and / have different behaviors for
    // negative numbers, so we need to jump through hoops to make sure
    // we don't divide negative numbers.
    if (i > -10) {
      i = -i;
      *p-- = '0' + char(i);
      *p = '-';
      return p;
    } else {
      // Make sure we aren't at MIN_INT, in which case we can't say i = -i
      i = i + 10;
      i = -i;
      *p-- = '0' + i % 10;
      // Undo what we did a moment ago
      i = i / 10 + 1;
      do {
        *p-- = '0' + i % 10;
        i /= 10;
      } while (i > 0);
      *p = '-';
      return p;
    }
  }
}

// Offset into buffer where FastInt32ToBuffer places the end of string
// null character.  Also used by FastInt32ToBufferLeft
static const int kFastInt32ToBufferOffset = 11;

// Yes, this is a duplicate of FastInt64ToBuffer.  But, we need this for the
// compiler to generate 32 bit arithmetic instructions.  It's much faster, at
// least with 32 bit binaries.
char *FastInt32ToBuffer(int32_t i, char* buffer) {
  // We could collapse the positive and negative sections, but that
  // would be slightly slower for positive numbers...
  // 12 bytes is enough to store -2**32, -4294967296.
  char* p = buffer + kFastInt32ToBufferOffset;
  *p-- = '\0';
  if (i >= 0) {
    do {
      *p-- = '0' + i % 10;
      i /= 10;
    } while (i > 0);
    return p + 1;
  } else {
    // On different platforms, % and / have different behaviors for
    // negative numbers, so we need to jump through hoops to make sure
    // we don't divide negative numbers.
    if (i > -10) {
      i = -i;
      *p-- = '0' + i;
      *p = '-';
      return p;
    } else {
      // Make sure we aren't at MIN_INT, in which case we can't say i = -i
      i = i + 10;
      i = -i;
      *p-- = '0' + i % 10;
      // Undo what we did a moment ago
      i = i / 10 + 1;
      do {
        *p-- = '0' + i % 10;
        i /= 10;
      } while (i > 0);
      *p = '-';
      return p;
    }
  }
}

char *FastHexToBuffer(int i, char* buffer) {
  // GOOGLE_CHECK(i >= 0) << "FastHexToBuffer() wants non-negative integers, not " << i;

  static const char *hexdigits = "0123456789abcdef";
  char *p = buffer + 21;
  *p-- = '\0';
  do {
    *p-- = hexdigits[i & 15];   // mod by 16
    i >>= 4;                    // divide by 16
  } while (i > 0);
  return p + 1;
}

char *InternalFastHexToBuffer(uint64_t value, char* buffer, int num_byte) {
  static const char *hexdigits = "0123456789abcdef";
  buffer[num_byte] = '\0';
  for (int i = num_byte - 1; i >= 0; i--) {
#ifdef _M_X64
    // MSVC x64 platform has a bug optimizing the uint32(value) in the #else
    // block. Given that the uint32 cast was to improve performance on 32-bit
    // platforms, we use 64-bit '&' directly.
    buffer[i] = hexdigits[value & 0xf];
#else
    buffer[i] = hexdigits[uint32_t(value) & 0xf];
#endif
    value >>= 4;
  }
  return buffer;
}

char *FastHex64ToBuffer(uint64_t value, char* buffer) {
  return InternalFastHexToBuffer(value, buffer, 16);
}

char *FastHex32ToBuffer(uint32_t value, char* buffer) {
  return InternalFastHexToBuffer(value, buffer, 8);
}

// ----------------------------------------------------------------------
// FastInt32ToBufferLeft()
// FastUInt32ToBufferLeft()
// FastInt64ToBufferLeft()
// FastUInt64ToBufferLeft()
//
// Like the Fast*ToBuffer() functions above, these are intended for speed.
// Unlike the Fast*ToBuffer() functions, however, these functions write
// their output to the beginning of the buffer (hence the name, as the
// output is left-aligned).  The caller is responsible for ensuring that
// the buffer has enough space to hold the output.
//
// Returns a pointer to the end of the string (i.e. the null character
// terminating the string).
// ----------------------------------------------------------------------

static const char two_ASCII_digits[100][2] = {
  {'0','0'}, {'0','1'}, {'0','2'}, {'0','3'}, {'0','4'},
  {'0','5'}, {'0','6'}, {'0','7'}, {'0','8'}, {'0','9'},
  {'1','0'}, {'1','1'}, {'1','2'}, {'1','3'}, {'1','4'},
  {'1','5'}, {'1','6'}, {'1','7'}, {'1','8'}, {'1','9'},
  {'2','0'}, {'2','1'}, {'2','2'}, {'2','3'}, {'2','4'},
  {'2','5'}, {'2','6'}, {'2','7'}, {'2','8'}, {'2','9'},
  {'3','0'}, {'3','1'}, {'3','2'}, {'3','3'}, {'3','4'},
  {'3','5'}, {'3','6'}, {'3','7'}, {'3','8'}, {'3','9'},
  {'4','0'}, {'4','1'}, {'4','2'}, {'4','3'}, {'4','4'},
  {'4','5'}, {'4','6'}, {'4','7'}, {'4','8'}, {'4','9'},
  {'5','0'}, {'5','1'}, {'5','2'}, {'5','3'}, {'5','4'},
  {'5','5'}, {'5','6'}, {'5','7'}, {'5','8'}, {'5','9'},
  {'6','0'}, {'6','1'}, {'6','2'}, {'6','3'}, {'6','4'},
  {'6','5'}, {'6','6'}, {'6','7'}, {'6','8'}, {'6','9'},
  {'7','0'}, {'7','1'}, {'7','2'}, {'7','3'}, {'7','4'},
  {'7','5'}, {'7','6'}, {'7','7'}, {'7','8'}, {'7','9'},
  {'8','0'}, {'8','1'}, {'8','2'}, {'8','3'}, {'8','4'},
  {'8','5'}, {'8','6'}, {'8','7'}, {'8','8'}, {'8','9'},
  {'9','0'}, {'9','1'}, {'9','2'}, {'9','3'}, {'9','4'},
  {'9','5'}, {'9','6'}, {'9','7'}, {'9','8'}, {'9','9'}
};

char* FastUInt32ToBufferLeft(uint32_t u, char* buffer) {
  uint32_t digits;
  const char *ASCII_digits = nullptr;
  // The idea of this implementation is to trim the number of divides to as few
  // as possible by using multiplication and subtraction rather than mod (%),
  // and by outputting two digits at a time rather than one.
  // The huge-number case is first, in the hopes that the compiler will output
  // that case in one branch-free block of code, and only output conditional
  // branches into it from below.
  if (u >= 1000000000) {  // >= 1,000,000,000
    digits = u / 100000000;  // 100,000,000
    ASCII_digits = two_ASCII_digits[digits];
    buffer[0] = ASCII_digits[0];
    buffer[1] = ASCII_digits[1];
    buffer += 2;
sublt100_000_000:
    u -= digits * 100000000;  // 100,000,000
lt100_000_000:
    digits = u / 1000000;  // 1,000,000
    ASCII_digits = two_ASCII_digits[digits];
    buffer[0] = ASCII_digits[0];
    buffer[1] = ASCII_digits[1];
    buffer += 2;
sublt1_000_000:
    u -= digits * 1000000;  // 1,000,000
lt1_000_000:
    digits = u / 10000;  // 10,000
    ASCII_digits = two_ASCII_digits[digits];
    buffer[0] = ASCII_digits[0];
    buffer[1] = ASCII_digits[1];
    buffer += 2;
sublt10_000:
    u -= digits * 10000;  // 10,000
lt10_000:
    digits = u / 100;
    ASCII_digits = two_ASCII_digits[digits];
    buffer[0] = ASCII_digits[0];
    buffer[1] = ASCII_digits[1];
    buffer += 2;
sublt100:
    u -= digits * 100;
lt100:
    digits = u;
    ASCII_digits = two_ASCII_digits[digits];
    buffer[0] = ASCII_digits[0];
    buffer[1] = ASCII_digits[1];
    buffer += 2;
done:
    *buffer = 0;
    return buffer;
  }

  if (u < 100) {
    digits = u;
    if (u >= 10) goto lt100;
    *buffer++ = '0' + digits;
    goto done;
  }
  if (u  <  10000) {   // 10,000
    if (u >= 1000) goto lt10_000;
    digits = u / 100;
    *buffer++ = '0' + digits;
    goto sublt100;
  }
  if (u  <  1000000) {   // 1,000,000
    if (u >= 100000) goto lt1_000_000;
    digits = u / 10000;  //    10,000
    *buffer++ = '0' + digits;
    goto sublt10_000;
  }
  if (u  <  100000000) {   // 100,000,000
    if (u >= 10000000) goto lt100_000_000;
    digits = u / 1000000;  //   1,000,000
    *buffer++ = '0' + digits;
    goto sublt1_000_000;
  }
  // we already know that u < 1,000,000,000
  digits = u / 100000000;   // 100,000,000
  *buffer++ = '0' + digits;
  goto sublt100_000_000;
}

char* FastInt32ToBufferLeft(int32_t i, char* buffer) {
  uint32_t u = 0;
  if (i < 0) {
    *buffer++ = '-';
    u -= i;
  } else {
    u = i;
  }
  return FastUInt32ToBufferLeft(u, buffer);
}

char* FastUInt64ToBufferLeft(uint64_t u64, char* buffer) {
  int digits;
  const char *ASCII_digits = nullptr;

  uint32_t u = static_cast<uint32_t>(u64);
  if (u == u64) return FastUInt32ToBufferLeft(u, buffer);

  uint64_t top_11_digits = u64 / 1000000000;
  buffer = FastUInt64ToBufferLeft(top_11_digits, buffer);
  u = uint32_t(u64 - (top_11_digits * 1000000000));

  digits = u / 10000000;  // 10,000,000
  // GOOGLE_DCHECK_LT(digits, 100);
  ASCII_digits = two_ASCII_digits[digits];
  buffer[0] = ASCII_digits[0];
  buffer[1] = ASCII_digits[1];
  buffer += 2;
  u -= digits * 10000000;  // 10,000,000
  digits = u / 100000;  // 100,000
  ASCII_digits = two_ASCII_digits[digits];
  buffer[0] = ASCII_digits[0];
  buffer[1] = ASCII_digits[1];
  buffer += 2;
  u -= digits * 100000;  // 100,000
  digits = u / 1000;  // 1,000
  ASCII_digits = two_ASCII_digits[digits];
  buffer[0] = ASCII_digits[0];
  buffer[1] = ASCII_digits[1];
  buffer += 2;
  u -= digits * 1000;  // 1,000
  digits = u / 10;
  ASCII_digits = two_ASCII_digits[digits];
  buffer[0] = ASCII_digits[0];
  buffer[1] = ASCII_digits[1];
  buffer += 2;
  u -= digits * 10;
  digits = u;
  *buffer++ = '0' + digits;
  *buffer = 0;
  return buffer;
}

char* FastInt64ToBufferLeft(int64_t i, char* buffer) {
  uint64_t u = 0;
  if (i < 0) {
    *buffer++ = '-';
    u -= i;
  } else {
    u = i;
  }
  return FastUInt64ToBufferLeft(u, buffer);
}

// ----------------------------------------------------------------------
// SimpleItoa()
//    Description: converts an integer to a string.
//
//    Return value: string
// ----------------------------------------------------------------------

std::string SimpleItoa(int i) {
  char buffer[kFastToBufferSize];
  return (sizeof(i) == 4) ?
    FastInt32ToBuffer(i, buffer) :
    FastInt64ToBuffer(i, buffer);
}

std::string SimpleItoa(unsigned int i) {
  char buffer[kFastToBufferSize];
  return std::string(buffer, (sizeof(i) == 4)
                                 ? FastUInt32ToBufferLeft(i, buffer)
                                 : FastUInt64ToBufferLeft(i, buffer));
}

std::string SimpleItoa(long i) {
  char buffer[kFastToBufferSize];
  return (sizeof(i) == 4) ?
    FastInt32ToBuffer(i, buffer) :
    FastInt64ToBuffer(i, buffer);
}

std::string SimpleItoa(unsigned long i) {
  char buffer[kFastToBufferSize];
  return std::string(buffer, (sizeof(i) == 4)
                                 ? FastUInt32ToBufferLeft(i, buffer)
                                 : FastUInt64ToBufferLeft(i, buffer));
}

std::string SimpleItoa(long long i) {
  char buffer[kFastToBufferSize];
  return (sizeof(i) == 4) ?
    FastInt32ToBuffer(int32_t(i), buffer) :
    FastInt64ToBuffer(i, buffer);
}

std::string SimpleItoa(unsigned long long i) {
  char buffer[kFastToBufferSize];
  return std::string(buffer, (sizeof(i) == 4)
                                 ? FastUInt32ToBufferLeft(uint32_t(i), buffer)
                                 : FastUInt64ToBufferLeft(i, buffer));
}

// ----------------------------------------------------------------------
// SimpleDtoa()
// SimpleFtoa()
// DoubleToBuffer()
// FloatToBuffer()
//    We want to print the value without losing precision, but we also do
//    not want to print more digits than necessary.  This turns out to be
//    trickier than it sounds.  Numbers like 0.2 cannot be represented
//    exactly in binary.  If we print 0.2 with a very large precision,
//    e.g. "%.50g", we get "0.2000000000000000111022302462515654042363167".
//    On the other hand, if we set the precision too low, we lose
//    significant digits when printing numbers that actually need them.
//    It turns out there is no precision value that does the right thing
//    for all numbers.
//
//    Our strategy is to first try printing with a precision that is never
//    over-precise, then parse the result with strtod() to see if it
//    matches.  If not, we print again with a precision that will always
//    give a precise result, but may use more digits than necessary.
//
//    An arguably better strategy would be to use the algorithm described
//    in "How to Print Floating-Point Numbers Accurately" by Steele &
//    White, e.g. as implemented by David M. Gay's dtoa().  It turns out,
//    however, that the following implementation is about as fast as
//    DMG's code.  Furthermore, DMG's code locks mutexes, which means it
//    will not scale well on multi-core machines.  DMG's code is slightly
//    more accurate (in that it will never use more digits than
//    necessary), but this is probably irrelevant for most users.
//
//    Rob Pike and Ken Thompson also have an implementation of dtoa() in
//    third_party/fmt/fltfmt.cc.  Their implementation is similar to this
//    one in that it makes guesses and then uses strtod() to check them.
//    Their implementation is faster because they use their own code to
//    generate the digits in the first place rather than use snprintf(),
//    thus avoiding format string parsing overhead.  However, this makes
//    it considerably more complicated than the following implementation,
//    and it is embedded in a larger library.  If speed turns out to be
//    an issue, we could re-implement this in terms of their
//    implementation.
// ----------------------------------------------------------------------

std::string SimpleDtoa(double value) {
  char buffer[kDoubleToBufferSize];
  return DoubleToBuffer(value, buffer);
}

std::string SimpleFtoa(float value) {
  char buffer[kFloatToBufferSize];
  return FloatToBuffer(value, buffer);
}

static inline bool IsValidFloatChar(char c) {
  return ('0' <= c && c <= '9') ||
         c == 'e' || c == 'E' ||
         c == '+' || c == '-';
}

void DelocalizeRadix(char* buffer) {
  // Fast check:  if the buffer has a normal decimal point, assume no
  // translation is needed.
  if (strchr(buffer, '.') != nullptr) return;

  // Find the first unknown character.
  while (IsValidFloatChar(*buffer)) ++buffer;

  if (*buffer == '\0') {
    // No radix character found.
    return;
  }

  // We are now pointing at the locale-specific radix character.  Replace it
  // with '.'.
  *buffer = '.';
  ++buffer;

  if (!IsValidFloatChar(*buffer) && *buffer != '\0') {
    // It appears the radix was a multi-byte character.  We need to remove the
    // extra bytes.
    char* target = buffer;
    do { ++buffer; } while (!IsValidFloatChar(*buffer) && *buffer != '\0');
    memmove(target, buffer, strlen(buffer) + 1);
  }
}

char* DoubleToBuffer(double value, char* buffer) {
  // DBL_DIG is 15 for IEEE-754 doubles, which are used on almost all
  // platforms these days.  Just in case some system exists where DBL_DIG
  // is significantly larger -- and risks overflowing our buffer -- we have
  // this assert.
  static_assert(DBL_DIG < 20, "DBL_DIG_is_too_big");

  if (value == std::numeric_limits<double>::infinity()) {
    strncpy(buffer, "inf", 3);
    return buffer;
  } else if (value == -std::numeric_limits<double>::infinity()) {
    strncpy(buffer, "-inf", 4);
    return buffer;
  } else if (std::isnan(value)) {
    strncpy(buffer, "nan", 3);
    return buffer;
  }

  int snprintf_result =
    snprintf(buffer, kDoubleToBufferSize, "%.*g", DBL_DIG, value);

  // The snprintf should never overflow because the buffer is significantly
  // larger than the precision we asked for.
  // GOOGLE_DCHECK(snprintf_result > 0 && snprintf_result < kDoubleToBufferSize);

  // We need to make parsed_value volatile in order to force the compiler to
  // write it out to the stack.  Otherwise, it may keep the value in a
  // register, and if it does that, it may keep it as a long double instead
  // of a double.  This long double may have extra bits that make it compare
  // unequal to "value" even though it would be exactly equal if it were
  // truncated to a double.
  volatile double parsed_value = strtod(buffer, nullptr);
  if (parsed_value != value) {
    snprintf_result =
        snprintf(buffer, kDoubleToBufferSize, "%.*g", DBL_DIG + 2, value);

    // Should never overflow; see above.
    // GOOGLE_DCHECK(snprintf_result > 0 && snprintf_result < kDoubleToBufferSize);
  }

  DelocalizeRadix(buffer);
  return buffer;
}

bool safe_strtof(const char* str, float* value) {
    char* endptr;
    errno = 0;  // errno only gets set on errors
    *value = strtof(str, &endptr);
    return *str != 0 && *endptr == 0 && errno == 0;
}

char* FloatToBuffer(float value, char* buffer) {
  // FLT_DIG is 6 for IEEE-754 floats, which are used on almost all
  // platforms these days.  Just in case some system exists where FLT_DIG
  // is significantly larger -- and risks overflowing our buffer -- we have
  // this assert.
  static_assert(FLT_DIG < 10, "FLT_DIG_is_too_big");

  if (value == std::numeric_limits<double>::infinity()) {
    strncpy(buffer, "inf", 3);
    return buffer;
  } else if (value == -std::numeric_limits<double>::infinity()) {
    strncpy(buffer, "-inf", 4);
    return buffer;
  } else if (std::isnan(value)) {
    strncpy(buffer, "nan", 3);
    return buffer;
  }

  int snprintf_result =
    snprintf(buffer, kFloatToBufferSize, "%.*g", FLT_DIG, value);

  // The snprintf should never overflow because the buffer is significantly
  // larger than the precision we asked for.
  // GOOGLE_DCHECK(snprintf_result > 0 && snprintf_result < kFloatToBufferSize);

  float parsed_value;
  if (!safe_strtof(buffer, &parsed_value) || parsed_value != value) {
    snprintf_result =
        snprintf(buffer, kFloatToBufferSize, "%.*g", FLT_DIG + 3, value);

    // Should never overflow; see above.
    // GOOGLE_DCHECK(snprintf_result > 0 && snprintf_result < kFloatToBufferSize);
  }

  DelocalizeRadix(buffer);
  return buffer;
}

namespace strings {

AlphaNum::AlphaNum(strings::Hex hex) {
  char *const end = &digits[kFastToBufferSize];
  char *writer = end;
  uint64_t value = hex.value;
  uint64_t width = hex.spec;
  // We accomplish minimum width by OR'ing in 0x10000 to the user's value,
  // where 0x10000 is the smallest hex number that is as wide as the user
  // asked for.
  uint64_t mask = (static_cast<uint64_t>(1) << ((width - 1) * 4)) | value;
  static const char hexdigits[] = "0123456789abcdef";
  do {
    *--writer = hexdigits[value & 0xF];
    value >>= 4;
    mask >>= 4;
  } while (mask != 0);
  piece_data_ = writer;
  piece_size_ = end - writer;
}

}  // namespace strings

// ----------------------------------------------------------------------
// StrCat()
//    This merges the given strings or integers, with no delimiter.  This
//    is designed to be the fastest possible way to construct a string out
//    of a mix of raw C strings, C++ strings, and integer values.
// ----------------------------------------------------------------------

// Append is merely a version of memcpy that returns the address of the byte
// after the area just overwritten.  It comes in multiple flavors to minimize
// call overhead.
static char *Append1(char *out, const AlphaNum &x) {
  if (x.size() > 0) {
    memcpy(out, x.data(), x.size());
    out += x.size();
  }
  return out;
}

static char *Append2(char *out, const AlphaNum &x1, const AlphaNum &x2) {
  if (x1.size() > 0) {
    memcpy(out, x1.data(), x1.size());
    out += x1.size();
  }
  if (x2.size() > 0) {
    memcpy(out, x2.data(), x2.size());
    out += x2.size();
  }
  return out;
}

static char *Append4(char *out, const AlphaNum &x1, const AlphaNum &x2,
                     const AlphaNum &x3, const AlphaNum &x4) {
  if (x1.size() > 0) {
    memcpy(out, x1.data(), x1.size());
    out += x1.size();
  }
  if (x2.size() > 0) {
    memcpy(out, x2.data(), x2.size());
    out += x2.size();
  }
  if (x3.size() > 0) {
    memcpy(out, x3.data(), x3.size());
    out += x3.size();
  }
  if (x4.size() > 0) {
    memcpy(out, x4.data(), x4.size());
    out += x4.size();
  }
  return out;
}

std::string StrCat(const AlphaNum &a, const AlphaNum &b) {
  std::string result;
  result.resize(a.size() + b.size());
  char *const begin = &*result.begin();
  char *out = Append2(begin, a, b);
  //GOOGLE_DCHECK_EQ(out, begin + result.size());
  return result;
}

std::string StrCat(const AlphaNum &a, const AlphaNum &b, const AlphaNum &c) {
  std::string result;
  result.resize(a.size() + b.size() + c.size());
  char *const begin = &*result.begin();
  char *out = Append2(begin, a, b);
  out = Append1(out, c);
  //GOOGLE_DCHECK_EQ(out, begin + result.size());
  return result;
}

std::string StrCat(const AlphaNum &a, const AlphaNum &b, const AlphaNum &c,
                   const AlphaNum &d) {
  std::string result;
  result.resize(a.size() + b.size() + c.size() + d.size());
  char *const begin = &*result.begin();
  char *out = Append4(begin, a, b, c, d);
  //GOOGLE_DCHECK_EQ(out, begin + result.size());
  return result;
}

std::string StrCat(const AlphaNum &a, const AlphaNum &b, const AlphaNum &c,
                   const AlphaNum &d, const AlphaNum &e) {
  std::string result;
  result.resize(a.size() + b.size() + c.size() + d.size() + e.size());
  char *const begin = &*result.begin();
  char *out = Append4(begin, a, b, c, d);
  out = Append1(out, e);
  //GOOGLE_DCHECK_EQ(out, begin + result.size());
  return result;
}

std::string StrCat(const AlphaNum &a, const AlphaNum &b, const AlphaNum &c,
                   const AlphaNum &d, const AlphaNum &e, const AlphaNum &f) {
  std::string result;
  result.resize(a.size() + b.size() + c.size() + d.size() + e.size() +
                f.size());
  char *const begin = &*result.begin();
  char *out = Append4(begin, a, b, c, d);
  out = Append2(out, e, f);
  //GOOGLE_DCHECK_EQ(out, begin + result.size());
  return result;
}

std::string StrCat(const AlphaNum &a, const AlphaNum &b, const AlphaNum &c,
                   const AlphaNum &d, const AlphaNum &e, const AlphaNum &f,
                   const AlphaNum &g) {
  std::string result;
  result.resize(a.size() + b.size() + c.size() + d.size() + e.size() +
                f.size() + g.size());
  char *const begin = &*result.begin();
  char *out = Append4(begin, a, b, c, d);
  out = Append2(out, e, f);
  out = Append1(out, g);
  //GOOGLE_DCHECK_EQ(out, begin + result.size());
  return result;
}

std::string StrCat(const AlphaNum &a, const AlphaNum &b, const AlphaNum &c,
                   const AlphaNum &d, const AlphaNum &e, const AlphaNum &f,
                   const AlphaNum &g, const AlphaNum &h) {
  std::string result;
  result.resize(a.size() + b.size() + c.size() + d.size() + e.size() +
                f.size() + g.size() + h.size());
  char *const begin = &*result.begin();
  char *out = Append4(begin, a, b, c, d);
  out = Append4(out, e, f, g, h);
  //GOOGLE_DCHECK_EQ(out, begin + result.size());
  return result;
}

std::string StrCat(const AlphaNum &a, const AlphaNum &b, const AlphaNum &c,
                   const AlphaNum &d, const AlphaNum &e, const AlphaNum &f,
                   const AlphaNum &g, const AlphaNum &h, const AlphaNum &i) {
  std::string result;
  result.resize(a.size() + b.size() + c.size() + d.size() + e.size() +
                f.size() + g.size() + h.size() + i.size());
  char *const begin = &*result.begin();
  char *out = Append4(begin, a, b, c, d);
  out = Append4(out, e, f, g, h);
  out = Append1(out, i);
  //GOOGLE_DCHECK_EQ(out, begin + result.size());
  return result;
}


void StrAppend(std::string *result, const AlphaNum &a) {
  //GOOGLE_DCHECK_NO_OVERLAP(*result, a);
  result->append(a.data(), a.size());
}

void StrAppend(std::string *result, const AlphaNum &a, const AlphaNum &b) {
  //GOOGLE_DCHECK_NO_OVERLAP(*result, a);
  //GOOGLE_DCHECK_NO_OVERLAP(*result, b);
  std::string::size_type old_size = result->size();
  result->resize(old_size + a.size() + b.size());
  char *const begin = &*result->begin();
  char *out = Append2(begin + old_size, a, b);
  //GOOGLE_DCHECK_EQ(out, begin + result->size());
}

void StrAppend(std::string *result, const AlphaNum &a, const AlphaNum &b,
               const AlphaNum &c) {
  //GOOGLE_DCHECK_NO_OVERLAP(*result, a);
  //GOOGLE_DCHECK_NO_OVERLAP(*result, b);
  //GOOGLE_DCHECK_NO_OVERLAP(*result, c);
  std::string::size_type old_size = result->size();
  result->resize(old_size + a.size() + b.size() + c.size());
  char *const begin = &*result->begin();
  char *out = Append2(begin + old_size, a, b);
  out = Append1(out, c);
  //GOOGLE_DCHECK_EQ(out, begin + result->size());
}

void StrAppend(std::string *result, const AlphaNum &a, const AlphaNum &b,
               const AlphaNum &c, const AlphaNum &d) {
  //GOOGLE_DCHECK_NO_OVERLAP(*result, a);
  //GOOGLE_DCHECK_NO_OVERLAP(*result, b);
  //GOOGLE_DCHECK_NO_OVERLAP(*result, c);
  //GOOGLE_DCHECK_NO_OVERLAP(*result, d);
  std::string::size_type old_size = result->size();
  result->resize(old_size + a.size() + b.size() + c.size() + d.size());
  char *const begin = &*result->begin();
  char *out = Append4(begin + old_size, a, b, c, d);
  //GOOGLE_DCHECK_EQ(out, begin + result->size());
}

int GlobalReplaceSubstring(const std::string &substring,
                           const std::string &replacement, std::string *s) {
  //GOOGLE_CHECK(s != nullptr);
  if (s->empty() || substring.empty())
    return 0;
  std::string tmp;
  int num_replacements = 0;
  size_t pos = 0;
  for (StringPiece::size_type match_pos =
           s->find(substring.data(), pos, substring.length());
       match_pos != std::string::npos; pos = match_pos + substring.length(),
                              match_pos = s->find(substring.data(), pos,
                                                  substring.length())) {
    ++num_replacements;
    // Append the original content before the match.
    tmp.append(*s, pos, match_pos - pos);
    // Append the replacement for the match.
    tmp.append(replacement.begin(), replacement.end());
  }
  // Append the content after the last match. If no replacements were made, the
  // original string is left untouched.
  if (num_replacements > 0) {
    tmp.append(*s, pos, s->length() - pos);
    s->swap(tmp);
  }
  return num_replacements;
}

uint32_t ghtonl(uint32_t x) {
    union {
        uint32_t result;
        uint8_t result_array[4];
    };
    result_array[0] = static_cast<uint8_t>(x >> 24);
    result_array[1] = static_cast<uint8_t>((x >> 16) & 0xFF);
    result_array[2] = static_cast<uint8_t>((x >> 8) & 0xFF);
    result_array[3] = static_cast<uint8_t>(x & 0xFF);
    return result;
}

// Helper to append a Unicode code point to a string as UTF8, without bringing
// in any external dependencies.
int EncodeAsUTF8Char(uint32_t code_point, char* output) {
  uint32_t tmp = 0;
  int len = 0;
  if (code_point <= 0x7f) {
    tmp = code_point;
    len = 1;
  } else if (code_point <= 0x07ff) {
    tmp = 0x0000c080 |
        ((code_point & 0x07c0) << 2) |
        (code_point & 0x003f);
    len = 2;
  } else if (code_point <= 0xffff) {
    tmp = 0x00e08080 |
        ((code_point & 0xf000) << 4) |
        ((code_point & 0x0fc0) << 2) |
        (code_point & 0x003f);
    len = 3;
  } else {
    // UTF-16 is only defined for code points up to 0x10FFFF, and UTF-8 is
    // normally only defined up to there as well.
    tmp = 0xf0808080 |
        ((code_point & 0x1c0000) << 6) |
        ((code_point & 0x03f000) << 4) |
        ((code_point & 0x000fc0) << 2) |
        (code_point & 0x003f);
    len = 4;
  }
  tmp = ghtonl(tmp);
  memcpy(output, reinterpret_cast<const char*>(&tmp) + sizeof(tmp) - len, len);
  return len;
}

// Table of UTF-8 character lengths, based on first byte
static const unsigned char kUTF8LenTbl[256] = {
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,

    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2,
    2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
    3, 3, 4, 4, 4, 4, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1};

// Return length of a single UTF-8 source character
int UTF8FirstLetterNumBytes(const char* src, int len) {
  if (len == 0) {
    return 0;
  }
  return kUTF8LenTbl[*reinterpret_cast<const uint8_t*>(src)];
}

// ----------------------------------------------------------------------
// CleanStringLineEndings()
//   Clean up a multi-line string to conform to Unix line endings.
//   Reads from src and appends to dst, so usually dst should be empty.
//
//   If there is no line ending at the end of a non-empty string, it can
//   be added automatically.
//
//   Four different types of input are correctly handled:
//
//     - Unix/Linux files: line ending is LF: pass through unchanged
//
//     - DOS/Windows files: line ending is CRLF: convert to LF
//
//     - Legacy Mac files: line ending is CR: convert to LF
//
//     - Garbled files: random line endings: convert gracefully
//                      lonely CR, lonely LF, CRLF: convert to LF
//
//   @param src The multi-line string to convert
//   @param dst The converted string is appended to this string
//   @param auto_end_last_line Automatically terminate the last line
//
//   Limitations:
//
//     This does not do the right thing for CRCRLF files created by
//     broken programs that do another Unix->DOS conversion on files
//     that are already in CRLF format.  For this, a two-pass approach
//     brute-force would be needed that
//
//       (1) determines the presence of LF (first one is ok)
//       (2) if yes, removes any CR, else convert every CR to LF

void CleanStringLineEndings(const std::string &src, std::string *dst,
                            bool auto_end_last_line) {
  if (dst->empty()) {
    dst->append(src);
    CleanStringLineEndings(dst, auto_end_last_line);
  } else {
    std::string tmp = src;
    CleanStringLineEndings(&tmp, auto_end_last_line);
    dst->append(tmp);
  }
}

inline uint64_t GOOGLE_UNALIGNED_LOAD64(const void* p) {
    uint64_t t;
    memcpy(&t, p, sizeof t);
    return t;
}

inline void GOOGLE_UNALIGNED_STORE64(void* p, uint64_t v) {
    memcpy(p, &v, sizeof v);
}

void CleanStringLineEndings(std::string *str, bool auto_end_last_line) {
  ptrdiff_t output_pos = 0;
  bool r_seen = false;
  ptrdiff_t len = str->size();

  char *p = &(*str)[0];

  for (ptrdiff_t input_pos = 0; input_pos < len;) {
    if (!r_seen && input_pos + 8 < len) {
      uint64_t v = GOOGLE_UNALIGNED_LOAD64(p + input_pos);
      // Loop over groups of 8 bytes at a time until we come across
      // a word that has a byte whose value is less than or equal to
      // '\r' (i.e. could contain a \n (0x0a) or a \r (0x0d) ).
      //
      // We use a has_less macro that quickly tests a whole 64-bit
      // word to see if any of the bytes has a value < N.
      //
      // For more details, see:
      //   http://graphics.stanford.edu/~seander/bithacks.html#HasLessInWord
#define has_less(x, n) (((x) - ~0ULL / 255 * (n)) & ~(x) & ~0ULL / 255 * 128)
      if (!has_less(v, '\r' + 1)) {
#undef has_less
        // No byte in this word has a value that could be a \r or a \n
        if (output_pos != input_pos) {
          GOOGLE_UNALIGNED_STORE64(p + output_pos, v);
        }
        input_pos += 8;
        output_pos += 8;
        continue;
      }
    }
    std::string::const_reference in = p[input_pos];
    if (in == '\r') {
      if (r_seen) p[output_pos++] = '\n';
      r_seen = true;
    } else if (in == '\n') {
      if (input_pos != output_pos)
        p[output_pos++] = '\n';
      else
        output_pos++;
      r_seen = false;
    } else {
      if (r_seen) p[output_pos++] = '\n';
      r_seen = false;
      if (input_pos != output_pos)
        p[output_pos++] = in;
      else
        output_pos++;
    }
    input_pos++;
  }
  if (r_seen ||
      (auto_end_last_line && output_pos > 0 && p[output_pos - 1] != '\n')) {
    str->resize(output_pos + 1);
    str->operator[](output_pos) = '\n';
  } else if (output_pos < len) {
    str->resize(output_pos);
  }
}
