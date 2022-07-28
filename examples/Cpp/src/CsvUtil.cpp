// Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

#include "CsvUtil.h"
#include <fstream>
#include "Range.h"
#include "StringUtil.h"


static int parseNextColumn(StringPiece& line, StringPiece& field, int delim, int quote)
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
                field = line.subpiece(start, pos - start);
                line.advance(pos - start + 2);
            }
            else { // end of line
                field = line.subpiece(start, pos - start);
                line.advance(pos - start + 1);
            }
            return (int)pos;
        }
        if (!in_quote && line[pos] == delim) {
            field = line.subpiece(start, pos - start);
            line.advance(pos - start + 1);
            return (int)pos;
        }
    }
    field = line.subpiece(start, pos);
    return -1;
}

static std::vector<StringPiece> parseLineToRows(StringPiece line, int delim=',', int quote='"')
{
    std::vector<StringPiece> row;
    int pos = 0;
    while (!line.empty()) {
        StringPiece field;
        int n = parseNextColumn(line, field, delim, quote);
        row.push_back(field);
        if (n < 0) {
            break;
        }
    }
    return row;
}

static std::vector<StringPiece> splitContentToLines(StringPiece content) {
    std::vector<StringPiece> lines;
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
        StringPiece line = content.subpiece(begin, end - begin);
        line = trimWhitespace(line);
        if (!line.empty()) {
            lines.push_back(line);
        }
    }
    return lines;
}

int ReadCsvRecord(const std::string& filename, std::vector<Record>& out)
{
    std::ifstream infile(filename.c_str());
    std::vector<StringPiece> header;
    std::string line;
    while (std::getline(infile, line)) {
        auto row = parseLineToRows(line);
        if (header.empty())
        {
            header = row;
        }
        Record record;
        for (size_t i = 0; i < row.size(); i++ )
        {
            const std::string& key = header[i].str();
            record[key] = row[i].str();
        }
        out.push_back(record);
    }
}

int RecordToKVMap(const std::vector<Record>& records, Record& out)
{
    for (size_t i = 0; i < records.size(); i++ )
    {
        auto record = records[i];
        out[record["Key"]] = record["Value"];
    }
}
