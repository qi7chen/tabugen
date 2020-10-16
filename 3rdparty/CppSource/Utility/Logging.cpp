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

#include "Logging.h"
#include <stdio.h>
#include <mutex>
#include <chrono>
#include <stdarg.h>
#include "StringUtil.h"


#if defined(_WIN32)
#include <Windows.h>
#elif defined(__ANDROID__)
#include <android/log.h>
#endif

using std::mutex;
using std::lock_guard;


namespace detail {

void DefaultLogHandler(LogLevel level, const char* filename, int line,
                       const std::string& message)
{
    static const char* level_names[] = { "DEBUG","INFO", "WARNING", "ERROR", "FATAL" };
#ifdef _WIN32
    const char* sep = strrchr(filename, '\\');
    if (sep)
    {
        filename = sep + 1;
    }
#endif
    auto msg = stringPrintf("[%s %s:%d] %s\n", level_names[level], filename,
        line, message.c_str());
#if defined(__ANDROID__)
    android_LogPriority priority = ANDROID_LOG_DEFAULT;
    switch (level)
    {
    case LOGLEVEL_DEBUG:
        priority = ANDROID_LOG_DEBUG;
        break;
    case LOGLEVEL_INFO:
        priority = ANDROID_LOG_INFO;
        break;
    case LOGLEVEL_WARNING:
        priority = ANDROID_LOG_WARN;
        break;
    case LOGLEVEL_ERROR:
        priority = ANDROID_LOG_ERROR;
        break;
    case LOGLEVEL_FATAL:
        priority = ANDROID_LOG_FATAL;
        break;
    }
    __android_log_print(priority, "xnet", "%s", msg.c_str());
#else
    fprintf(stderr, "%s\n", msg.c_str());
#endif //_WIN32
}

void NullLogHandler(LogLevel /* level */, const char* /* filename */,
                    int /* line */, const std::string& /* message */)
{
    // Nothing.
}

typedef void LogHandler(LogLevel level, const char* filename, int line,
    const std::string& message);

static LogHandler* log_handler_ = &DefaultLogHandler;
static int log_silencer_count_ = 0;
static mutex log_silencer_count_mutex_;

void LogMessage::Finish() {
    bool suppress = false;

    if (level_ != LOGLEVEL_FATAL) {
        lock_guard<mutex> lock(log_silencer_count_mutex_);
        suppress = log_silencer_count_ > 0;
    }

    if (!suppress) {
        log_handler_(level_, filename_, line_, strm_.str());
    }

    if (level_ == LOGLEVEL_FATAL) {
#ifdef _WIN32
        MessageBoxA(NULL, strm_.str().c_str(), "Fatal", MB_OK);
#endif
        abort(); // TODO: add stack backtrace
    }
}

void LogFinisher::operator=(LogMessage& other) {
    other.Finish();
}

LogHandler* GetDefaultLogHandler()
{
    return log_handler_;
}

} // namespace detail
