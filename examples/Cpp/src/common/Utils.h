// Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

#pragma once

#include <string>
#include <vector>
#include <unordered_map>

// Read csv file to key-value records
typedef std::unordered_map<std::string, std::string> Record;

int ReadCsvRecord(const std::string& filename, std::vector<Record>& out);

int RecordToKVMap(const std::vector<Record>& records, Record& out);
