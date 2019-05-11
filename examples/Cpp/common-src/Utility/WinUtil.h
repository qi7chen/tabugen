// Copyright 2018-preset ichenq@outlook.com. All Rights Reserved.
// Any redistribution or reproduction of part or all of the contents in any form
// is prohibited.
//
// You may not, except with our express written permission, distribute or commercially
// exploit the content. Nor may you transmit it or store it in any other website or
// other form of electronic retrieval system.

#pragma once

#if defined(_WIN32)

#include <string>
#include <windows.h>
//
// Windows platform only utility functions
//

// Get string description of an error code
std::string GetLastErrorMessage(DWORD dwError);

// Encode text between multibyte (both GBK and UTF-8) and wide characters (UCS-2, a subset of UTF-16)
std::wstring MultibyteToWide(const std::string& strMultibyte, unsigned int codePage = CP_ACP);
std::string WideToMultibyte(const std::wstring& strWide, unsigned int codePage = CP_ACP);

inline std::string GBKToUtf8(const std::string& strText)
{
    return WideToMultibyte(MultibyteToWide(strText), CP_UTF8);
}

void OutputStringToDebugger(const std::string& message);

#endif // _WIN32
