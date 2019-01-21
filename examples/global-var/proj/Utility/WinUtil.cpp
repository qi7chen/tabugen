// Copyright 2018-preset Beyondtech Inc. All Rights Reserved.
//
// Any redistribution or reproduction of part or all of the contents in any form
// is prohibited.
//
// You may not, except with our express written permission, distribute or commercially
// exploit the content. Nor may you transmit it or store it in any other website or
// other form of electronic retrieval system.


#include "WinUtil.h"
#include <algorithm>

#if defined(_WIN32)

std::string GetLastErrorMessage(DWORD dwError)
{
    // this should be thread local
    char szText[1024] = {};
    DWORD dwRet = FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, dwError, 0, szText, 1024, NULL);
    szText[dwRet] = '\0';
    return std::string(szText, dwRet);
}

std::wstring MultibyteToWide(const std::string& strMultibyte, unsigned int codePage /*= CP_ACP*/)
{
    std::wstring strWide;
    int count = MultiByteToWideChar(codePage, 0, strMultibyte.data(), (int)strMultibyte.length(), NULL, 0);
    if (count > 0)
    {
        strWide.resize(count);
        MultiByteToWideChar(codePage, 0, strMultibyte.data(), (int)strMultibyte.length(),
            const_cast<wchar_t*>(strWide.data()), (int)strWide.length());
    }
    return strWide;
}

std::string WideToMultibyte(const std::wstring& strWide, unsigned int codePage /*= CP_ACP*/)
{
    std::string strMultibyte;
    int count = WideCharToMultiByte(codePage, 0, strWide.data(), (int)strWide.length(), NULL, 0, NULL, NULL);
    if (count > 0)
    {
        strMultibyte.resize(count);
        WideCharToMultiByte(codePage, 0, strWide.data(), (int)strWide.length(),
            const_cast<char*>(strMultibyte.data()), (int)strMultibyte.length(), NULL, NULL);
    }
    return strMultibyte;
}


const size_t MAX_OUTPUT_LEN = 4032;

void OutputStringToDebugger(const std::string& message)
{
    const std::wstring& text = MultibyteToWide(message, CP_UTF8);
    if (text.size() < MAX_OUTPUT_LEN) //common case
    {
        OutputDebugStringW(text.c_str());
        return;
    }
    size_t outputed = 0;
    while (outputed < text.size())
    {
        // maximum length accepted
        // see http://www.unixwiz.net/techtips/outputdebugstring.html
        wchar_t buf[MAX_OUTPUT_LEN] = {};
        size_t left = text.size() - outputed;
        wcsncpy(buf, text.c_str() + outputed, std::min(left, MAX_OUTPUT_LEN - 1));
        OutputDebugStringW(buf);
        if (left >= MAX_OUTPUT_LEN - 1)
        {
            outputed += MAX_OUTPUT_LEN - 1;
        }
        else
        {
            outputed += left;
        }
    }
}

#endif // _WIN32
