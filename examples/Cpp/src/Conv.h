// Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

#pragma once

#include <cmath>
#include <cstdlib>
#include <string>
#include <algorithm>
#include <type_traits>
#include "StringUtil.h"


#define FB_STRINGIZE(x)     #x

#define FOLLY_RANGE_CHECK(condition, message, src)          \
  ((condition) ? (void)0 : throw std::range_error(          \
    (std::string(FB_STRINGIZE(__FILE__) "(" FB_STRINGIZE(__LINE__) "): ") \
     + (message) + ": '" + (src) + "'").c_str()))


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
}

/**
 * The identity conversion function.
 * to<T>(T) returns itself for all types T.
 */
template <class Tgt, class Src>
typename std::enable_if<std::is_same<Tgt, Src>::value, Tgt>::type
to(const Src& value) {
	return value;
}

template <class Tgt, class Src>
typename std::enable_if<
	std::is_same<Tgt, typename std::decay<Src>::type>::value,
	Tgt>::type
to(Src&& value) {
	return std::forward<Src>(value);
}

/*******************************************************************************
 * Arithmetic to boolean
 ******************************************************************************/

template <class Tgt, class Src>
typename std::enable_if<
	std::is_arithmetic<Src>::value && !std::is_same<Tgt, Src>::value&&
	std::is_same<Tgt, bool>::value,
	Tgt>::type
to(const Src& value) {
	return value != Src();
}


/*******************************************************************************
 * Integral to integral
 ******************************************************************************/

template <class Tgt, class Src>
typename std::enable_if<
	std::is_integral<Src>::value
	&& std::is_integral<Tgt>::value
	&& !std::is_same<Tgt, Src>::value,
	Tgt>::type
to(const Src& value)
{
	/* static */ if (std::numeric_limits<Tgt>::max()
		< std::numeric_limits<Src>::max())
	{
		FOLLY_RANGE_CHECK(
			value <= std::numeric_limits<Tgt>::max(),
			"Overflow", std::to_string(value));
	}
	/* static */ if (std::is_signed<Src>::value &&
		(!std::is_signed<Tgt>::value || sizeof(Src) > sizeof(Tgt)))
	{
		FOLLY_RANGE_CHECK(
			value >= std::numeric_limits<Tgt>::min(),
			"Negative overflow", std::to_string(value));
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
to(const Src& value)
{
	/* static */ if (std::numeric_limits<Tgt>::max() <
		std::numeric_limits<Src>::max())
	{
		FOLLY_RANGE_CHECK(value <= std::numeric_limits<Tgt>::max(),
			"Overflow", std::to_string(value));
		FOLLY_RANGE_CHECK(value >= -std::numeric_limits<Tgt>::max(),
			"Negative overflow", std::to_string(value));
	}
	return detail::implicit_cast<Tgt>(value);
}

/*******************************************************************************
 * anything to string type.
 ******************************************************************************/

template <class Tgt, class Src>
typename std::enable_if<
    std::is_same<Tgt, std::string>::value, Tgt>::type
to(const Src& value)
{
    Tgt result = std::to_string(value);
    return std::move(result);
}


/*******************************************************************************
 * string integral types.
 ******************************************************************************/

template <class Tgt, class Src>
typename std::enable_if<
    std::is_integral<Tgt>::value
    && std::is_signed<Tgt>::value
    && !std::is_same<typename std::remove_cv<Tgt>::type, bool>::value,
    Tgt>::type
to(StringPiece s)
{
    int64_t n = std::strtoll(s.data(), nullptr, 10);
    return to<Tgt>(n);
}

template <class Tgt, class Src>
typename std::enable_if<
    std::is_integral<Tgt>::value
    && std::is_unsigned<Tgt>::value
    && !std::is_same<typename std::remove_cv<Tgt>::type, bool>::value,
    Tgt>::type
to(StringPiece s)
{
    uint64_t n = std::strtoull(s.data(), nullptr, 10);
    return to<Tgt>(n);
}

/*******************************************************************************
 * string to floating types.
 ******************************************************************************/

template <class Tgt, class Src>
typename std::enable_if<
    std::is_floating_point<Tgt>::value,
    Tgt>::type
to(StringPiece s)
{
    double f = 0;
    safe_strtod(s, &f);
    return to<Tgt>(f);
}

/*******************************************************************************
 * string to bool type.
 ******************************************************************************/

template <class Tgt>
typename std::enable_if<
    std::is_same<typename std::remove_cv<Tgt>::type, bool>::value,
    Tgt>::type
to(StringPiece s)
{
    bool b = false;
    safe_strtob(s, &b);
    return b;
}


/*******************************************************************************
 * Integral to floating point and back
 ******************************************************************************/

template <class Tgt, class Src>
typename std::enable_if<
	(std::is_integral<Src>::value&& std::is_floating_point<Tgt>::value)
	||
	(std::is_floating_point<Src>::value && std::is_integral<Tgt>::value),
	Tgt>::type
to(const Src& value)
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
to(const Src& value)
{
	return to<Tgt>(static_cast<typename std::underlying_type<Src>::type>(value));
}

template <class Tgt, class Src>
typename std::enable_if<
	std::is_enum<Tgt>::value && !std::is_same<Src, Tgt>::value, Tgt>::type
to(const Src& value)
{
	return static_cast<Tgt>(to<typename std::underlying_type<Tgt>::type>(value));
}

