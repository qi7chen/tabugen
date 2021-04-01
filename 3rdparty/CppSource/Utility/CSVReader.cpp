// Copyright (C) 2020-present ichenq@outlook.com. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

#include "CSVReader.h"
#include <assert.h>
#include <stdio.h>
#include "StringUtil.h"

#ifndef ASSERT
#define ASSERT assert
#endif

CSVReader::CSVReader(int delimiter, int quote)
    : quote_(quote), delimiter_(delimiter)
{
}

long CSVReader::ReadFileContent(const char* filepath)
{
    ASSERT(filepath != nullptr);
    // We open the file in binary mode as it makes no difference under *nix
    // and under Windows we handle \r\n newlines ourself.
    FILE* fp = std::fopen(filepath, "rb");
    if (fp == NULL)
    {
        return -1;
    }
    content_.clear();
    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    if (size == 0) {
        fclose(fp);
        return 0;
    }
    fseek(fp, 0, SEEK_SET);
    content_.resize(size);
    fread(&content_[0], 1, size, fp);
    fclose(fp);
    return size;
}


std::vector<StringPiece> CSVReader::ParseContentToLines()
{
    std::vector<StringPiece> lines;
    size_t pos = 0;
    if (buffer_.size() >= 3 && buffer_[0] == '\xEF' && buffer_[1] == '\xBB' && buffer_[2] == '\xBF') {
        pos = 3;
    }
    while (pos < buffer_.size()) {
        size_t begin = pos;
        while (buffer_[pos] != '\n') {
            pos++;
        }
        size_t end = pos;
        if (end > begin && buffer_[end - 1] == '\r') {
            end--;
        }
        pos = end + 1;
        StringPiece line = buffer_.subpiece(begin, end - begin);
        line = trimWhitespace(line);
        if (!line.empty()) {
            lines.push_back(line);
        }
    }
    return lines;
}

std::vector<StringPiece> CSVReader::ParseLineToRow(StringPiece line)
{
    std::vector<StringPiece> row;
    int pos = 0;
    while (!line.empty()) {
        StringPiece field;
        int n = ParseNextColumn(line, field);
        row.push_back(field);
        if (n < 0) {
            break;
        }
    }
    return row;
}

int CSVReader::ParseNextColumn(StringPiece& line, StringPiece& field)
{
    bool in_quote = false;
    size_t start = 0;
    if (line[start] == quote_) {
        in_quote = true;
        start++;
    }
    size_t pos = start;
    for (; pos < line.size(); pos++) {
        if (in_quote && line[pos] == quote_) {
            if (pos + 1 < line.size() && line[pos + 1] == delimiter_) {
                field = line.subpiece(start, pos - start);
                line.advance(pos + 2);
            }
            else { // end of line
                field = line.subpiece(start, pos - start);
                line.advance(pos + 1);
            }
            return (int)pos;
        }
        if (!in_quote && line[pos] == delimiter_) {
            field = line.subpiece(start, pos - start);
            line.advance(pos + 1);
            return (int)pos;
        }
    }
    field = line.subpiece(start, pos);
    return -1;
}

void CSVReader::ParseFile(const std::string& filename)
{
    ReadFileContent(filename.c_str());
    buffer_ = content_;
    Parse();
}

void CSVReader::Parse(StringPiece content)
{
    buffer_ = content;
    Parse();
}

void CSVReader::Parse()
{
    auto lines = ParseContentToLines();
    for (auto& line : lines)
    {
        auto row = ParseLineToRow(line);
        rows_.push_back(row);
    }
}
