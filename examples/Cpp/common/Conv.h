// Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

#pragma once

#include <string>
#include <sstream>
#include <vector>
#include <algorithm>
#include <type_traits>
#include <absl/strings/str_cat.h>
#include <absl/strings/numbers.h>


/**
 * Use FB_STRINGIZE(x) when you'd want to do what #x does inside
 * another macro expansion.
 */
#define FB_STRINGIZE(x) #x


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
	to(const Src& value)
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

inline void toAppend(std::string* result, absl::string_view value)
{
	assert(result);
	result->append(value.data(), value.size());
}

/**
 * A single char gets appended.
 */
inline void toAppend(std::string* result, char value) {
	*result += value;
}

template <class Src>
typename std::enable_if <
	std::is_integral<Src>::value > ::type
	toAppend(std::string* result, Src value) {
	absl::StrAppend(result, value);
}

/**
 * As above, but for floating point
 */
template <class Src>
typename std::enable_if<
	std::is_floating_point<Src>::value>::type
	toAppend(std::string* result, Src value)
{
	absl::StrAppend(result, value);
}

/**
 * Variadic base case: do nothing.
 */
inline void toAppend(std::string*) {}

/**
 * Enumerated values get appended as integers.
 */
template <class Tgt, class Src>
typename std::enable_if<
	std::is_enum<Src>::value>::type
	toAppend(Tgt* result, Src value) {
	toAppend(result, typename std::underlying_type<Tgt>::type(value));
}

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

 /**
  * string_view to integrals
  */
template <class Tgt>
typename std::enable_if<
	std::is_integral<Tgt>::value &&
	sizeof(Tgt) >= 4 &&
	!std::is_same<typename std::remove_cv<Tgt>::type, bool>::value,
	Tgt>::type
	to(absl::string_view src) {
	Tgt result = 0;
	if (absl::SimpleAtoi<Tgt>(src, &result)) {
		return result;
	}
	return 0;
}

template <class Tgt>
typename std::enable_if <
	std::is_integral<Tgt>::value &&
	sizeof(Tgt) < 4 &&
	!std::is_same<typename std::remove_cv<Tgt>::type, bool>::value,
	Tgt > ::type
	to(absl::string_view src) {
	int result = 0;
	if (absl::SimpleAtoi(src, &result)) {
		return to<Tgt>(result);
	}
	return 0;
}

/**
 * string_view to bool
 */
template <class Tgt>
typename std::enable_if<
	std::is_same<typename std::remove_cv<Tgt>::type, bool>::value,
	Tgt>::type
	to(absl::string_view src)
{
	bool result = false;
	if (absl::SimpleAtob(src, &result)) {
		return result;
	}
	return false;
}

/**
 * string_view to float
 */
template <class Tgt>
typename std::enable_if<
	std::is_same<typename std::remove_cv<Tgt>::type, float>::value,
	Tgt>::type
	to(absl::string_view src)
{
	float result = 0.0f;
	if (absl::SimpleAtof(src, &result)) {
		return result;
	}
	return 0.0f;
}

/**
 * string_view to float
 */
template <class Tgt>
typename std::enable_if<
	std::is_same<typename std::remove_cv<Tgt>::type, double>::value,
	Tgt>::type
	to(absl::string_view src)
{
	double result = 0.0;
	if (absl::SimpleAtod(src, &result)) {
		return result;
	}
	return 0.0;
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
