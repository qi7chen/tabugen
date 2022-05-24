// Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

#include "Utils.h"
#include <absl/strings/ascii.h>

static int parseNextColumn(absl::string_view& line, absl::string_view& field, int delim, int quote)
{
    bool in_quote = false;
    size_t start = 0;
    if (line[start] == quote) {
        in_quote = true;
        start++;
    }
    size_t pos = start;
    for (; pos < line.size(); pos++) {
        if (in_quote && line[pos] == quote) {
            if (pos + 1 < line.size() && line[pos + 1] == delim) {
                field = line.substr(start, pos - start);
                line.remove_prefix(pos + 2);
            }
            else { // end of line
                field = line.substr(start, pos - start);
                line.remove_prefix(pos + 1);
            }
            return (int)pos;
        }
        if (!in_quote && line[pos] == delim) {
            field = line.substr(start, pos - start);
            line.remove_prefix(pos + 1);
            return (int)pos;
        }
    }
    field = line.substr(start, pos);
    return -1;
}

std::vector<absl::string_view> parseLineToRows(absl::string_view line, int delim, int quote)
{
    std::vector<absl::string_view> row;
    int pos = 0;
    while (!line.empty()) {
        absl::string_view field;
        int n = parseNextColumn(line, field, delim, quote);
        row.push_back(field);
        if (n < 0) {
            break;
        }
    }
    return row;
}

std::vector<absl::string_view> splitContentToLines(absl::string_view content) {
    std::vector<absl::string_view> lines;
    size_t pos = 0;
    // UTF8-BOM
    if (content.size() >= 3 && content[0] == '\xEF' && content[1] == '\xBB' && content[2] == '\xBF') {
        pos = 3;
    }
    while (pos < content.size()) {
        size_t begin = pos;
        while (content[pos] != '\n') {
            pos++;
        }
        size_t end = pos;
        if (end > begin && content[end - 1] == '\r') {
            end--;
        }
        pos = end + 1;
        absl::string_view line = content.substr(begin, end - begin);
        line = absl::StripAsciiWhitespace(line);
        if (!line.empty()) {
            lines.push_back(line);
        }
    }
    return lines;
}
