/*
 * Copyright 2015-present Facebook, Inc.
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

#include "Range.h"
#include <bitset>

namespace detail {

size_t qfind_first_byte_of_bitset(const StringPiece haystack, const StringPiece needles)
{
    std::bitset<256> s;
    for (auto needle : needles) {
        s[(uint8_t)needle] = true;
    }
    for (size_t index = 0; index < haystack.size(); ++index) {
        if (s[(uint8_t)haystack[index]]) {
            return index;
        }
    }
    return std::string::npos;
}

} // namespace detail


#ifdef _DEBUG

// mock gtest API
#define EXPECT_TRUE(expr)   assert(expr)
#define EXPECT_FALSE(expr)  assert(!expr)
#define EXPECT_EQ(a, b)     assert(a == b)
#define EXPECT_NE(a, b)     assert(a != b)
#define EXPECT_LT(a, b)     assert(a < b)
#define EXPECT_LE(a, b)     assert(a <= b)
#define EXPECT_GT(a, b)     assert(a > b)
#define EXPECT_GE(a, b)     assert(a >= b)

void TestRangeAll()
{
    using namespace std;

    const char* foo = "foo";
    const char* foo2 = "foo";
    string fooStr(foo);
    string foo2Str(foo2);

    // we expect the compiler to optimize things so that there's only one copy
    // of the string literal "foo", even though we've got it in multiple places
    EXPECT_EQ(foo, foo2); // remember, this uses ==, not strcmp, so it's a ptr
    // comparison rather than lexical

    // the string object creates copies though, so the c_str of these should be
    // distinct
    EXPECT_NE(fooStr.c_str(), foo2Str.c_str());

    // test the basic StringPiece functionality
    StringPiece s(foo);
    EXPECT_EQ(s.size(), 3);

    EXPECT_EQ(s.start(), foo); // ptr comparison
    EXPECT_NE(s.start(), fooStr.c_str()); // ptr comparison
    EXPECT_NE(s.start(), foo2Str.c_str()); // ptr comparison

    EXPECT_EQ(s.toString(), foo); // lexical comparison
    EXPECT_EQ(s.toString(), fooStr.c_str()); // lexical comparison
    EXPECT_EQ(s.toString(), foo2Str.c_str()); // lexical comparison

    EXPECT_EQ(s, foo); // lexical comparison
    EXPECT_EQ(s, fooStr); // lexical comparison
    EXPECT_EQ(s, foo2Str); // lexical comparison
    EXPECT_EQ(foo, s);

    // check using StringPiece to reference substrings
    const char* foobarbaz = "foobarbaz";

    // the full "foobarbaz"
    s.reset(foobarbaz, strlen(foobarbaz));
    EXPECT_EQ(s.size(), 9);
    EXPECT_EQ(s.start(), foobarbaz);
    EXPECT_EQ(s, "foobarbaz");

    // only the 'foo'
    s.assign(foobarbaz, foobarbaz + 3);
    EXPECT_EQ(s.size(), 3);
    EXPECT_EQ(s.start(), foobarbaz);
    EXPECT_EQ(s, "foo");

    // find
    s.reset(foobarbaz, strlen(foobarbaz));
    EXPECT_EQ(s.find("bar"), 3);
    EXPECT_EQ(s.find("ba", 3), 3);
    EXPECT_EQ(s.find("ba", 4), 6);
    EXPECT_EQ(s.find("notfound"), StringPiece::npos);
    EXPECT_EQ(s.find("notfound", 1), StringPiece::npos);
    EXPECT_EQ(s.find("bar", 4), StringPiece::npos); // starting position too far
    // starting pos that is obviously past the end -- This works for std::string
    EXPECT_EQ(s.toString().find("notfound", 55), StringPiece::npos);
    EXPECT_EQ(s.find("z", s.size()), StringPiece::npos);
    EXPECT_EQ(s.find("z", 55), StringPiece::npos);
    // empty needle
    EXPECT_EQ(s.find(""), std::string().find(""));
    EXPECT_EQ(s.find(""), 0);

    // single char finds
    EXPECT_EQ(s.find('b'), 3);
    EXPECT_EQ(s.find('b', 3), 3);
    EXPECT_EQ(s.find('b', 4), 6);
    EXPECT_EQ(s.find('o', 2), 2);
    EXPECT_EQ(s.find('y'), StringPiece::npos);
    EXPECT_EQ(s.find('y', 1), StringPiece::npos);
    EXPECT_EQ(s.find('o', 4), StringPiece::npos); // starting position too far
    EXPECT_TRUE(s.contains('z'));
    // starting pos that is obviously past the end -- This works for std::string
    EXPECT_EQ(s.toString().find('y', 55), StringPiece::npos);
    EXPECT_EQ(s.find('z', s.size()), StringPiece::npos);
    EXPECT_EQ(s.find('z', 55), StringPiece::npos);
    // null char
    EXPECT_EQ(s.find('\0'), std::string().find('\0'));
    EXPECT_EQ(s.find('\0'), StringPiece::npos);
    EXPECT_FALSE(s.contains('\0'));

    // single char rfinds
    EXPECT_EQ(s.rfind('b'), 6);
    EXPECT_EQ(s.rfind('y'), StringPiece::npos);
    EXPECT_EQ(s.str().rfind('y'), StringPiece::npos);
    EXPECT_EQ(ByteRange(s).rfind('b'), 6);
    EXPECT_EQ(ByteRange(s).rfind('y'), StringPiece::npos);
    // null char
    EXPECT_EQ(s.rfind('\0'), s.str().rfind('\0'));
    EXPECT_EQ(s.rfind('\0'), StringPiece::npos);

    // find_first_of
    s.reset(foobarbaz, strlen(foobarbaz));
    EXPECT_EQ(s.find_first_of("bar"), 3);
    EXPECT_EQ(s.find_first_of("ba", 3), 3);
    EXPECT_EQ(s.find_first_of("ba", 4), 4);
    EXPECT_TRUE(s.contains("bar"));
    EXPECT_EQ(s.find_first_of("xyxy"), StringPiece::npos);
    EXPECT_EQ(s.find_first_of("xyxy", 1), StringPiece::npos);
    EXPECT_FALSE(s.contains("xyxy"));
    // starting position too far
    EXPECT_EQ(s.find_first_of("foo", 4), StringPiece::npos);
    // starting pos that is obviously past the end -- This works for std::string
    EXPECT_EQ(s.toString().find_first_of("xyxy", 55), StringPiece::npos);
    EXPECT_EQ(s.find_first_of("z", s.size()), StringPiece::npos);
    EXPECT_EQ(s.find_first_of("z", 55), StringPiece::npos);
    // empty needle. Note that this returns npos, while find() returns 0!
    EXPECT_EQ(s.find_first_of(""), std::string().find_first_of(""));
    EXPECT_EQ(s.find_first_of(""), StringPiece::npos);

    // single char find_first_ofs
    EXPECT_EQ(s.find_first_of('b'), 3);
    EXPECT_EQ(s.find_first_of('b', 3), 3);
    EXPECT_EQ(s.find_first_of('b', 4), 6);
    EXPECT_EQ(s.find_first_of('o', 2), 2);
    EXPECT_EQ(s.find_first_of('y'), StringPiece::npos);
    EXPECT_EQ(s.find_first_of('y', 1), StringPiece::npos);
    // starting position too far
    EXPECT_EQ(s.find_first_of('o', 4), StringPiece::npos);
    // starting pos that is obviously past the end -- This works for std::string
    EXPECT_EQ(s.toString().find_first_of('y', 55), StringPiece::npos);
    EXPECT_EQ(s.find_first_of('z', s.size()), StringPiece::npos);
    EXPECT_EQ(s.find_first_of('z', 55), StringPiece::npos);
    // null char
    EXPECT_EQ(s.find_first_of('\0'), std::string().find_first_of('\0'));
    EXPECT_EQ(s.find_first_of('\0'), StringPiece::npos);

    // just "barbaz"
    s.reset(foobarbaz + 3, strlen(foobarbaz + 3));
    EXPECT_EQ(s.size(), 6);
    EXPECT_EQ(s.start(), foobarbaz + 3);
    EXPECT_EQ(s, "barbaz");

    // just "bar"
    s.reset(foobarbaz + 3, 3);
    EXPECT_EQ(s.size(), 3);
    EXPECT_EQ(s, "bar");

    // clear
    s.clear();
    EXPECT_EQ(s.toString(), "");

    // test an empty StringPiece
    StringPiece s2;
    EXPECT_EQ(s2.size(), 0);

    // Test comparison operators
    foo = "";
    EXPECT_LE(s, foo);
    EXPECT_LE(foo, s);
    EXPECT_GE(s, foo);
    EXPECT_GE(foo, s);
    EXPECT_EQ(s, foo);
    EXPECT_EQ(foo, s);

    foo = "abc";
    EXPECT_LE(s, foo);
    EXPECT_LT(s, foo);
    EXPECT_GE(foo, s);
    EXPECT_GT(foo, s);
    EXPECT_NE(s, foo);

    EXPECT_LE(s, s);
    EXPECT_LE(s, s);
    EXPECT_GE(s, s);
    EXPECT_GE(s, s);
    EXPECT_EQ(s, s);
    EXPECT_EQ(s, s);

    s = "abc";
    s2 = "abc";
    EXPECT_LE(s, s2);
    EXPECT_LE(s2, s);
    EXPECT_GE(s, s2);
    EXPECT_GE(s2, s);
    EXPECT_EQ(s, s2);
    EXPECT_EQ(s2, s);
}

#endif // _DEBUG
