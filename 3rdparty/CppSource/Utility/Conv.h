/*
 * Copyright 2014 Facebook, Inc.
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

/**
 * Converts anything to anything, with an emphasis on performance and
 * safety.
 *
 * @author Andrei Alexandrescu (andrei.alexandrescu@fb.com)
 */

#pragma once

#include <stdint.h>
#include <assert.h>
#include <float.h>
#include <stdlib.h>
#include <string>
#include <sstream>
#include <typeinfo>
#include <stdexcept>
#include <algorithm>
#include <type_traits>
//#include "Portability.h"
#include "Preprocessor.h"
#include "Logging.h"
#include "Range.h"


#define FOLLY_RANGE_CHECK(condition, message, src)          \
  ((condition) ? (void)0 : throw std::range_error(          \
    (std::string(__FILE__ "(" FB_STRINGIZE(__LINE__) "): ") \
     + (message) + ": '" + (src) + "'").c_str()))

#define FOLLY_RANGE_CHECK_BEGIN_END(condition, message, b, e)    \
    FOLLY_RANGE_CHECK(condition, message, std::string((b), (e) - (b)))

#define FOLLY_RANGE_CHECK_STRINGPIECE(condition, message, sp)    \
    FOLLY_RANGE_CHECK(condition, message, std::string((sp).data(), (sp).size()))    


namespace detail {

// Use implicit_cast as a safe version of static_cast or const_cast
// for upcasting in the type hierarchy (i.e. casting a pointer to Foo
// to a pointer to SuperclassOfFoo or casting a pointer to Foo to
// a const pointer to Foo).
// When you use implicit_cast, the compiler checks that the cast is safe.
// Such explicit implicit_casts are necessary in surprisingly many
// situations where C++ demands an exact type match instead of an
// argument type convertable to a target type.
template<typename T> struct identity { typedef T type; };
template<typename Tgt> Tgt implicit_cast(typename identity<Tgt>::type t)
{
    return t;
}

template <typename T>
std::string to_string(const T& value) 
{
    std::stringstream strm;
    strm << value;
    return strm.str();
}

} // namespace detail


/**
 * The identity conversion function.
 * to<T>(T) returns itself for all types T.
 */
template <class Tgt, class Src>
typename std::enable_if<std::is_same<Tgt, Src>::value, Tgt>::type
to(const Src & value) {
  return value;
}

template <class Tgt, class Src>
typename std::enable_if<std::is_same<Tgt, Src>::value, Tgt>::type
to(Src && value) {
  return std::move(value);
}

/*******************************************************************************
 * Integral to integral
 ******************************************************************************/

/**
 * Checked conversion from integral to integral. The checks are only
 * performed when meaningful, e.g. conversion from int to long goes
 * unchecked.
 */
template <class Tgt, class Src>
typename std::enable_if<
    std::is_integral<Src>::value
    && std::is_integral<Tgt>::value
    && !std::is_same<Tgt, Src>::value,
    Tgt>::type
to(const Src & value)
{
    /* static */ if (std::numeric_limits<Tgt>::max()
        < std::numeric_limits<Src>::max()) 
    {
        FOLLY_RANGE_CHECK(
            value <= std::numeric_limits<Tgt>::max(),
            "Overflow", detail::to_string(value));
    }
    /* static */ if (std::is_signed<Src>::value &&
        (!std::is_signed<Tgt>::value || sizeof(Src) > sizeof(Tgt))) 
    {
        FOLLY_RANGE_CHECK(
            value >= std::numeric_limits<Tgt>::min(),
            "Negative overflow", detail::to_string(value));
    }
    return static_cast<Tgt>(value);
}

/*******************************************************************************
 * Floating point to floating point
 ******************************************************************************/

template <class Tgt, class Src>
typename std::enable_if<
  std::is_floating_point<Tgt>::value
  && std::is_floating_point<Src>::value
  && !std::is_same<Tgt, Src>::value,
  Tgt>::type
to(const Src & value) 
{
    /* static */ if (std::numeric_limits<Tgt>::max() <
        std::numeric_limits<Src>::max())
    {
        FOLLY_RANGE_CHECK(value <= std::numeric_limits<Tgt>::max(),
            "Overflow", detail::to_string(value));
        FOLLY_RANGE_CHECK(value >= -std::numeric_limits<Tgt>::max(),
            "Negative overflow", detail::to_string(value));
    }
    return detail::implicit_cast<Tgt>(value);
}

/*******************************************************************************
 * Conversions from integral types to string types.
 ******************************************************************************/

/**
 * Returns the number of digits in the base 10 representation of an
 * uint64_t. Useful for preallocating buffers and such. It's also used
 * internally, see below. Measurements suggest that defining a
 * separate overload for 32-bit integers is not worthwhile.
 */

inline uint32_t digits10(uint64_t v)
{
    uint32_t result = 1;
    for (;;)
    {
        if LIKELY((v < 10)) return result;
        if LIKELY((v < 100)) return result + 1;
        if LIKELY((v < 1000)) return result + 2;
        if LIKELY((v < 10000)) return result + 3;
        // Skip ahead by 4 orders of magnitude
        v /= 10000U;
        result += 4;
    }
}


/**
 * Copies the ASCII base 10 representation of v into buffer and
 * returns the number of bytes written. Does NOT append a \0. Assumes
 * the buffer points to digits10(v) bytes of valid memory. Note that
 * uint64 needs at most 20 bytes, uint32_t needs at most 10 bytes,
 * uint16_t needs at most 5 bytes, and so on. Measurements suggest
 * that defining a separate overload for 32-bit integers is not
 * worthwhile.
 *
 * This primitive is unsafe because it makes the size assumption and
 * because it does not add a terminating \0.
 */

inline uint32_t uint64ToBufferUnsafe(uint64_t v, char *const buffer)
{
    const auto result = digits10(v);
    // WARNING: using size_t or pointer arithmetic for pos slows down
    // the loop below 20x. This is because several 32-bit ops can be
    // done in parallel, but only fewer 64-bit ones.
    uint32_t pos = result - 1;
    while (v >= 10)
    {
        // Keep these together so a peephole optimization "sees" them and
        // computes them in one shot.
        const uint64_t q = v / 10;
        const uint32_t r = static_cast<uint32_t>(v % 10);
        buffer[pos--] = '0' + static_cast<uint8_t>(r);
        v = q;
    }
    // Last digit is trivial to handle
    buffer[pos] = static_cast<uint8_t>(v) + '0';
    return result;
}


/**
 * A single char gets appended.
 */
inline void toAppend(std::string* result, char value)
{
    DCHECK_NOTNULL(result);
    *result += value;
}

template<class T>
typename std::enable_if <
    std::is_same<T, char>::value,
    size_t > ::type
    estimateSpaceNeeded(T) 
{
    return 1;
}

/**
 * Everything implicitly convertible to const char* gets appended.
 */
template <class Src>
typename std::enable_if<
    std::is_convertible<Src, const char*>::value>::type
toAppend(std::string* result, Src value)
{
    DCHECK_NOTNULL(result);
    // Treat null pointers like an empty string, as in:
    // operator<<(std::ostream&, const char*).
    const char* c = value;
    if (c)
    {
        result->append(value);
    }
}

inline void toAppend(std::string* result, StringPiece value)
{
    DCHECK_NOTNULL(result);
    result->append(value.data(), value.size());
}

/**
 * int32_t and int64_t to string (by appending) go through here. The
 * result is APPENDED to a preexisting string passed as the second
 * parameter. This should be efficient with fbstring because fbstring
 * incurs no dynamic allocation below 23 bytes and no number has more
 * than 22 bytes in its textual representation (20 for digits, one for
 * sign, one for the terminating 0).
 */
template <class Src>
typename std::enable_if<
    std::is_integral<Src>::value
    && std::is_signed<Src>::value
    && sizeof(Src) >= 4>::type
toAppend(std::string* result, Src value)
{
    DCHECK_NOTNULL(result);
    char buffer[20];
    if (value < 0)
    {
        result->push_back('-');
        result->append(buffer, uint64ToBufferUnsafe(-int64_t(value), buffer));
    }
    else
    {
        result->append(buffer, uint64ToBufferUnsafe(value, buffer));
    }
}

/**
 * As above, but for uint32_t and uint64_t.
 */
template <class Src>
typename std::enable_if<
    std::is_integral<Src>::value
    && !std::is_signed<Src>::value
    && sizeof(Src) >= 4>::type
toAppend(std::string* result, Src value)
{
    DCHECK_NOTNULL(result);
    char buffer[20];
    result->append(buffer, buffer + uint64ToBufferUnsafe(value, buffer));
}

/**
 * All small signed and unsigned integers to string go through 32-bit
 * types int32_t and uint32_t, respectively.
 */
template <class Src>
typename std::enable_if<
    std::is_integral<Src>::value
    && sizeof(Src) < 4>::type
toAppend(std::string* result, Src value)
{
    DCHECK_NOTNULL(result);
    typedef typename
        std::conditional<std::is_signed<Src>::value,
        int64_t, uint64_t>::type Intermediate;
    toAppend(result, static_cast<Intermediate>(value));
}

/**
 * Enumerated values get appended as integers.
 */
template <class Src>
typename std::enable_if<
    std::is_enum<Src>::value>::type
toAppend(std::string* result, Src value)
{
    toAppend(result,
        static_cast<typename std::underlying_type<Src>::type>(value));
}

/*******************************************************************************
 * Conversions from floating-point types to string types.
 ******************************************************************************/

/**
 * As above, but for floating point
 */
template <class Src>
typename std::enable_if<
    std::is_floating_point<Src>::value>::type
toAppend(std::string* result, Src value)
{
    char buffer[32];
    int count = snprintf(buffer, 32, "%.2f", value);
    DCHECK(count > 0);
    for (int i = count - 1; i > 1; i--)
    {
        if (buffer[i] == '0' && buffer[i - 1] != '.')
            count--;
        else
            break;
    }
    toAppend(result, StringPiece(buffer, count));
}

/**
 * Variadic base case: do nothing.
 */
inline void toAppend(std::string* ) {}


/**
 * Variadic conversion to string. Appends each element in turn.
 */
template <class T, class... Ts>
typename std::enable_if<sizeof...(Ts) >= 1>::type
toAppend(std::string* result, const T& v, const Ts&... vs)
{
    toAppend(result, v);
    toAppend(result, vs...);
}

template <class Tgt, class... Ts>
typename std::enable_if<
    std::is_same<Tgt, std::string>::value && (sizeof...(Ts) >= 1),
    Tgt>::type
to(const Ts&... vs)
{
    Tgt result;
    toAppend(&result, vs...);
    return std::move(result);
}


/*******************************************************************************
 * Conversions from string types to integral types.
 ******************************************************************************/

namespace detail {

/**
 * Finds the first non-digit in a string. The number of digits
 * searched depends on the precision of the Tgt integral. Assumes the
 * string starts with NO whitespace and NO sign.
 *
 * The semantics of the routine is:
 *   for (;; ++b) {
 *     if (b >= e || !isdigit(*b)) return b;
 *   }
 *
 *  Complete unrolling marks bottom-line (i.e. entire conversion)
 *  improvements of 20%.
 */
template <class Tgt>
const char* findFirstNonDigit(const char* b, const char* e)
{
    DCHECK(b && e);
    for (; b < e; ++b)
    {
        auto const c = static_cast<unsigned>(*b) - '0';
        if (c >= 10)
            break;
    }
    return b;
}

// Maximum value of number when represented as a string
template <class T> struct MaxString
{
    static const char*const value;
};


/*
 * Lookup tables that converts from a decimal character value to an integral
 * binary value, shifted by a decimal "shift" multiplier.
 * For all character values in the range '0'..'9', the table at those
 * index locations returns the actual decimal value shifted by the multiplier.
 * For all other values, the lookup table returns an invalid OOR value.
 */

// Out-of-range flag value, larger than the largest value that can fit in
// four decimal bytes (9999), but four of these added up together should
// still not overflow uint16_t.
const int32_t OOR = 10000;

FOLLY_ALIGN(16) const uint16_t shift1[] =
{
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 0-9
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  10
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  20
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  30
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, 0,         //  40
    1, 2, 3, 4, 5, 6, 7, 8, 9, OOR, OOR,
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  60
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  70
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  80
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  90
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 100
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 110
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 120
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 130
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 140
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 150
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 160
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 170
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 180
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 190
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 200
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 210
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 220
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 230
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 240
    OOR, OOR, OOR, OOR, OOR, OOR                       // 250
};

FOLLY_ALIGN(16) const uint16_t shift10[] =
{
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 0-9
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  10
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  20
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  30
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, 0,         //  40
    10, 20, 30, 40, 50, 60, 70, 80, 90, OOR, OOR,
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  60
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  70
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  80
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  90
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 100
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 110
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 120
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 130
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 140
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 150
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 160
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 170
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 180
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 190
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 200
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 210
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 220
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 230
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 240
    OOR, OOR, OOR, OOR, OOR, OOR                       // 250
};

FOLLY_ALIGN(16) const uint16_t shift100[] =
{
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 0-9
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  10
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  20
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  30
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, 0,         //  40
    100, 200, 300, 400, 500, 600, 700, 800, 900, OOR, OOR,
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  60
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  70
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  80
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  90
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 100
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 110
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 120
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 130
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 140
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 150
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 160
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 170
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 180
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 190
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 200
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 210
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 220
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 230
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 240
    OOR, OOR, OOR, OOR, OOR, OOR                       // 250
};

FOLLY_ALIGN(16) const uint16_t shift1000[] =
{
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 0-9
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  10
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  20
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  30
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, 0,         //  40
    1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, OOR, OOR,
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  60
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  70
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  80
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  //  90
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 100
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 110
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 120
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 130
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 140
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 150
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 160
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 170
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 180
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 190
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 200
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 210
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 220
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 230
    OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR, OOR,  // 240
    OOR, OOR, OOR, OOR, OOR, OOR                       // 250
};

/**
 * String represented as a pair of pointers to char to unsigned
 * integrals. Assumes NO whitespace before or after, and also that the
 * string is composed entirely of digits. Tgt must be unsigned, and no
 * sign is allowed in the string (even it's '+'). String may be empty,
 * in which case digits_to throws.
 */
template <class Tgt>
Tgt digits_to(const char * b, const char * e)
{
    static_assert(!std::is_signed<Tgt>::value, "Unsigned type expected");
    assert(b <= e);

    const size_t size = e - b;

    /* Although the string is entirely made of digits, we still need to
     * check for overflow.
     */
    if (size >= std::numeric_limits<Tgt>::digits10 + 1)
    {
        // Leading zeros? If so, recurse to keep things simple
        if (b < e && *b == '0')
        {
            for (++b;; ++b)
            {
                if (b == e) return 0; // just zeros, e.g. "0000"
                if (*b != '0') return digits_to<Tgt>(b, e);
            }
        }
        FOLLY_RANGE_CHECK_BEGIN_END(
            size == std::numeric_limits<Tgt>::digits10 + 1 &&
            strncmp(b, detail::MaxString<Tgt>::value, size) <= 0,
            "Numeric overflow upon conversion", b, e);
    }

    // Here we know that the number won't overflow when
    // converted. Proceed without checks.
    Tgt result = 0;
    for (; e - b >= 4; b += 4)
    {
        result = static_cast<Tgt>(result * 10000);
        const int32_t r0 = shift1000[static_cast<size_t>(b[0])];
        const int32_t r1 = shift100[static_cast<size_t>(b[1])];
        const int32_t r2 = shift10[static_cast<size_t>(b[2])];
        const int32_t r3 = shift1[static_cast<size_t>(b[3])];
        const auto sum = r0 + r1 + r2 + r3;
        assert(sum < OOR && "Assumption: string only has digits");
        result += static_cast<Tgt>(sum);
    }

    switch (e - b)
    {
    case 3:
    {
        const int32_t r0 = shift100[static_cast<size_t>(b[0])];
        const int32_t r1 = shift10[static_cast<size_t>(b[1])];
        const int32_t r2 = shift1[static_cast<size_t>(b[2])];
        const auto sum = r0 + r1 + r2;
        assert(sum < OOR && "Assumption: string only has digits");
        return static_cast<Tgt>(result * 1000 + sum);
    }
    case 2:
    {
        const int32_t r0 = shift10[static_cast<size_t>(b[0])];
        const int32_t r1 = shift1[static_cast<size_t>(b[1])];
        const auto sum = r0 + r1;
        assert(sum < OOR && "Assumption: string only has digits");
        return static_cast<Tgt>(result * 100 + sum);
    }
    case 1:
        {
            const int32_t sum = shift1[static_cast<size_t>(b[0])];
            assert(sum < OOR && "Assumption: string only has digits");
            return static_cast<Tgt>(result * 10 + sum);
        }
    }

    assert(b == e);
    FOLLY_RANGE_CHECK_BEGIN_END(size > 0,
        "Found no digits to convert in input", b, e);
    return result;
}

bool str_to_bool(StringPiece * src);

/**
 * Enforce that the suffix following a number is made up only of whitespace.
 */
inline void enforceWhitespace(const char* b, const char* e) {
    for (; b != e; ++b) {
        FOLLY_RANGE_CHECK_BEGIN_END(isspace(*b),
            to<std::string>("Non-whitespace: ", *b),
            b, e);
    }
}


} // namespace detail

/**
 * String represented as a pair of pointers to char to unsigned
 * integrals. Assumes NO whitespace before or after.
 */
template <class Tgt>
typename std::enable_if<
    std::is_integral<Tgt>::value
    && !std::is_signed<Tgt>::value
    && !std::is_same<typename std::remove_cv<Tgt>::type, bool>::value,
    Tgt>::type
to(const char* b, const char* e)
{
    DCHECK(b && e);
    return detail::digits_to<Tgt>(b, e);
}

/**
 * String represented as a pair of pointers to char to signed
 * integrals. Assumes NO whitespace before or after. Allows an
 * optional leading sign.
 */
template <class Tgt>
typename std::enable_if<
    std::is_integral<Tgt>::value
    && std::is_signed<Tgt>::value,
    Tgt>::type
to(const char* b, const char* e)
{
    FOLLY_RANGE_CHECK(b < e, "Empty input string in conversion to integral",
        to<std::string>("b: ", intptr_t(b), " e: ", intptr_t(e)));
    if (!isdigit(*b))
    {
        if (*b == '-')
        {
            const auto r = to<typename std::make_unsigned<Tgt>::type>(b + 1, e);
            Tgt result = -static_cast<Tgt>(r);
            FOLLY_RANGE_CHECK_BEGIN_END(result <= 0, "Negative overflow.", b, e);
            return result;
        }
        FOLLY_RANGE_CHECK_BEGIN_END(*b == '+', "Invalid lead character", b, e);
        ++b;
    }
    Tgt result = to<typename std::make_unsigned<Tgt>::type>(b, e);
    FOLLY_RANGE_CHECK_BEGIN_END(result >= 0, "Overflow", b, e);
    return result;
}

/**
 * Parsing strings to integrals. These routines differ from
 * to<integral>(string) in that they take a POINTER TO a StringPiece
 * and alter that StringPiece to reflect progress information.
 */

/**
 * StringPiece to integrals, with progress information. Alters the
 * StringPiece parameter to munch the already-parsed characters.
 */
template <class Tgt>
typename std::enable_if<
    std::is_integral<Tgt>::value
    && !std::is_same<typename std::remove_cv<Tgt>::type, bool>::value,
    Tgt>::type
to(StringPiece* src)
{
    auto b = src->data(), past = src->data() + src->size();
    for (;; ++b)
    {
        FOLLY_RANGE_CHECK_STRINGPIECE(b < past,
            "No digits found in input string", *src);
        if (!isspace(*b)) break;
    }

    auto m = b;

    // First digit is customized because we test for sign
    bool negative = false;
    /* static */ if (std::is_signed<Tgt>::value)
    {
        if (!isdigit(*m))
        {
            if (*m == '-')
            {
                negative = true;
            }
            else
            {
                FOLLY_RANGE_CHECK_STRINGPIECE(*m == '+', "Invalid leading character in "
                    "conversion to integral", *src);
            }
            ++b;
            ++m;
        }
    }
    FOLLY_RANGE_CHECK_STRINGPIECE(m < past, "No digits found in input string",
        *src);
    FOLLY_RANGE_CHECK_STRINGPIECE(isdigit(*m), "Non-digit character found", *src);
    m = detail::findFirstNonDigit<Tgt>(m + 1, past);

    Tgt result;
    /* static */ if (!std::is_signed<Tgt>::value)
    {
        result = detail::digits_to<typename std::make_unsigned<Tgt>::type>(b, m);
    }
    else
    {
        auto t = detail::digits_to<typename std::make_unsigned<Tgt>::type>(b, m);
        if (negative)
        {
            result = -static_cast<Tgt>(t);
            FOLLY_RANGE_CHECK_STRINGPIECE(result <= 0,
                "Negative overflow", *src);
        }
        else
        {
            result = t;
            FOLLY_RANGE_CHECK_STRINGPIECE(result >= 0, "Overflow", *src);
        }
    }
    src->advance(m - src->data());
    return result;
}


/**
 * StringPiece to bool, with progress information. Alters the
 * StringPiece parameter to munch the already-parsed characters.
 */
template <class Tgt>
typename std::enable_if<
    std::is_same<typename std::remove_cv<Tgt>::type, bool>::value,
    Tgt>::type
to(StringPiece* src)
{
    return detail::str_to_bool(src);
}

/**
 * String or StringPiece to integrals. Accepts leading and trailing
 * whitespace, but no non-space trailing characters.
 */
template <class Tgt>
typename std::enable_if<
    std::is_integral<Tgt>::value,
    Tgt>::type
to(StringPiece src)
{
    Tgt result = to<Tgt>(&src);
    detail::enforceWhitespace(src.data(), src.data() + src.size());
    return result;
}


template <class Src>
typename std::enable_if<
    std::is_floating_point<Src>::value
    || std::is_integral<Src>::value,
    std::string>::type
toFixed(Src value)
{
    DCHECK(value != 0);
    std::string result(1, ' ');
    if (value > 0)
    {
        result.push_back('+');
    }
    toAppend(&result, value);
    auto pos = result.find('.');
    if (pos != std::string::npos)
    {
        if ((pos + 3) < result.size())
        {
            result.erase(pos + 3);
        }
        switch (result.size() - pos - 1)
        {
        case 1:
            if (result[pos + 1] == '0')
            {
                result.erase(pos);
            }
            break;
        case 2:
            if (result[pos + 1] == '0' && result[pos + 2] == '0')
            {
                result.erase(pos);
            }
            break;
        }
    }
    return result;
}



/*******************************************************************************
 * Conversions from string types to floating-point types.
 ******************************************************************************/

/**
 * StringPiece to double, with progress information. Alters the
 * StringPiece parameter to munch the already-parsed characters.
 */
template <class Tgt>
inline typename std::enable_if<
    std::is_floating_point<Tgt>::value,
    Tgt>::type
to(StringPiece *const src)
{
    FOLLY_RANGE_CHECK_STRINGPIECE(!src->empty(),
        "No digits found in input string", *src);

    char* end;
    double result = strtod(src->data(), &end);
    int length = static_cast<int>(end - src->data());
    if (length > 0 && !std::isnan(result))
    {
        src->advance(length);
        return result;
    }

    for (;; src->advance(1))
    {
        if (src->empty())
        {
            throw std::range_error("Unable to convert an empty string"
                " to a floating point value.");
        }
        if (!isspace(src->front())) {
            break;
        }
    }

    // Was that "inf[inity]"?
    if (src->size() >= 3 && toupper((*src)[0]) == 'I'
        && toupper((*src)[1]) == 'N' && toupper((*src)[2]) == 'F')
    {
        if (src->size() >= 8 &&
            toupper((*src)[3]) == 'I' &&
            toupper((*src)[4]) == 'N' &&
            toupper((*src)[5]) == 'I' &&
            toupper((*src)[6]) == 'T' &&
            toupper((*src)[7]) == 'Y')
        {
            src->advance(8);
        }
        else
        {
            src->advance(3);
        }
        return std::numeric_limits<Tgt>::infinity();
    }

    // Was that "-inf[inity]"?
    if (src->size() >= 4 && toupper((*src)[0]) == '-'
        && toupper((*src)[1]) == 'I' && toupper((*src)[2]) == 'N'
        && toupper((*src)[3]) == 'F')
    {
        if (src->size() >= 9 &&
            toupper((*src)[4]) == 'I' &&
            toupper((*src)[5]) == 'N' &&
            toupper((*src)[6]) == 'I' &&
            toupper((*src)[7]) == 'T' &&
            toupper((*src)[8]) == 'Y')
        {
            src->advance(9);
        }
        else
        {
            src->advance(4);
        }
        return -std::numeric_limits<Tgt>::infinity();
    }

    // "nan"?
    if (src->size() >= 3 && toupper((*src)[0]) == 'N'
        && toupper((*src)[1]) == 'A' && toupper((*src)[2]) == 'N')
    {
        src->advance(3);
        return std::numeric_limits<Tgt>::quiet_NaN();
    }

    // "-nan"?
    if (src->size() >= 4 &&
        toupper((*src)[0]) == '-' &&
        toupper((*src)[1]) == 'N' &&
        toupper((*src)[2]) == 'A' &&
        toupper((*src)[3]) == 'N')
    {
        src->advance(4);
        return -std::numeric_limits<Tgt>::quiet_NaN();
    }

    // All bets are off
    throw std::range_error("Unable to convert \"" + src->toString()
        + "\" to a floating point value.");
}


/**
 * Any string, const char*, or StringPiece to double.
 */
template <class Tgt>
typename std::enable_if<
    std::is_floating_point<Tgt>::value,
    Tgt>::type
to(StringPiece src)
{
    Tgt result = static_cast<Tgt>(to<double>(&src));
    detail::enforceWhitespace(src.data(), src.data() + src.size());
    return result;
}

/*******************************************************************************
 * Integral to floating point and back
 ******************************************************************************/

/**
 * Checked conversion from integral to flating point and back. The
 * result must be convertible back to the source type without loss of
 * precision. This seems Draconian but sometimes is what's needed, and
 * complements existing routines nicely. For various rounding
 * routines, see <math>.
 */
template <class Tgt, class Src>
typename std::enable_if<
    (std::is_integral<Src>::value && std::is_floating_point<Tgt>::value)
    ||
    (std::is_floating_point<Src>::value && std::is_integral<Tgt>::value),
    Tgt>::type
to(const Src & value)
{
    Tgt result = value;
    auto witness = static_cast<Src>(result);
    if (value != witness)
    {
        throw std::range_error(
            to<std::string>("to<>: loss of precision when converting ", value,
            " to type ", typeid(Tgt).name()).c_str());
    }
    return result;
}

/*******************************************************************************
 * Enum to anything and back
 ******************************************************************************/
template <class Tgt, class Src>
typename std::enable_if<
  std::is_enum<Src>::value && !std::is_same<Src, Tgt>::value, Tgt>::type
to(const Src & value) 
{
    return to<Tgt>(static_cast<typename std::underlying_type<Src>::type>(value));
}

template <class Tgt, class Src>
typename std::enable_if<
  std::is_enum<Tgt>::value && !std::is_same<Src, Tgt>::value, Tgt>::type
to(const Src & value) 
{
    return static_cast<Tgt>(to<typename std::underlying_type<Tgt>::type>(value));
}
