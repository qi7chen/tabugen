// Copyright (C) 2020-present ichenq@outlook.com. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

#pragma once

#include <vector>
#include "Range.h"

class CSVReader
{
public:
    typedef std::vector<std::vector<StringPiece>> Rows;
    explicit CSVReader(int delimiter = ',', int quote = '"');

    void Parse(StringPiece content);
    void ParseFile(const std::string& filename);

    const Rows& GetRows() { return rows_; }

private:
    void Parse();
    long ReadFileContent(const char* filepath);
    std::vector<StringPiece> ParseContentToLines();
    std::vector<StringPiece> ParseLineToRow(StringPiece line);
    int ParseNextColumn(StringPiece& line, StringPiece& field);

private:
    const int quote_ = '"';
    const int delimiter_ = ',';

    std::string     content_;
    StringPiece     buffer_;
    Rows            rows_;
};

