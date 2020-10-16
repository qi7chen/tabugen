# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

CPP_MANAGER_METHOD_TEMPLATE = """
    // Load all configurations
    static void LoadAll();

    // Clear all configurations
    static void ClearAll();

    // Read content from an asset file
    static std::string ReadFileContent(const char* filepath);

    // default loader
    static std::function<std::string(const char*)> reader;
"""


CPP_PARSE_FUN_TEMPLATE = """
// parse value from text
template <typename T>
inline T ParseValue(StringPiece text)
{
    text = trimWhitespace(text);
    if (text.empty())
    {
        return T();
    }
    return to<T>(text);
}

"""
