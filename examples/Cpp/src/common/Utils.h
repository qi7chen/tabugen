// Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

#pragma once

#include <string>
#include <vector>
#include <absl/strings/string_view.h>

// parse text line to delimiter-seperated rows
std::vector<absl::string_view> parseLineToRows(absl::string_view line, int delim = ',', int quote = '"');

// split content to lines
std::vector<absl::string_view> splitContentToLines(absl::string_view content);
