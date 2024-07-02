// Copyright (C) 2024 ki7chen@github. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

package config

import (
	"bytes"
	"cmp"
	"encoding/csv"
	"io"
	"log"
	"math"
	"os"
	"strconv"
	"strings"
)

// GDTable 数据表
type GDTable struct {
	HeadNames map[string]int32 // header name -> column index
	Rows      [][]string       // data rows
}

// ColSize 列数
func (t *GDTable) ColSize() int {
	return len(t.HeadNames)
}

// RowSize 行数
func (t *GDTable) RowSize() int {
	return len(t.Rows)
}

// GetCell 获取指定列（名称）指定行的数据
func (t *GDTable) GetCell(name string, rowIdx int) string {
	if rowIdx >= 0 && rowIdx < t.RowSize() {
		var row = t.Rows[rowIdx]
		var col = t.HeadNames[name]
		if col > 0 && int(col) <= len(row) {
			return row[col-1]
		}
	}
	return ""
}

// GetRow 获取指定行的所有数据
func (t *GDTable) GetRow(rowIdx int) []string {
	if rowIdx >= 0 && rowIdx < t.RowSize() {
		return t.Rows[rowIdx]
	}
	return nil
}

// HasColumn 是否有这列
func (t *GDTable) HasColumn(name string) bool {
    _, ok := t.HeadNames[name]
    return ok
}

// GetColumns 获取指定列的所有数据
func (t *GDTable) GetColumns(name string) []string {
	var col = t.HeadNames[name]
	if col > 0 {
		var result = make([]string, 0, t.RowSize())
		for _, row := range t.Rows {
			if int(col) <= len(row) {
				result = append(result, row[col-1])
			}
		}
		return result
	}
	return nil
}

// ToKVMap 转换为key-value形式的map
func (t *GDTable) ToKVMap() map[string]string {
	var keyCol = t.HeadNames["Key"]
	var ValCol = t.HeadNames["Value"]
	if keyCol < 0 || ValCol < 0 {
		return nil
	}
	var dict = make(map[string]string, len(t.Rows))
	for _, row := range t.Rows {
		if int(keyCol) <= len(row) && int(ValCol) <= len(row) {
			dict[row[keyCol-1]] = row[ValCol-1]
		}
	}
	return dict
}

// ReadCSVTable 读取CSV数据表
func ReadCSVTable(data []byte) (*GDTable, error) {
	var r = csv.NewReader(bytes.NewReader(data))
	var table = &GDTable{
		HeadNames: make(map[string]int32),
	}
	for i := 0; ; i++ {
		row, err := r.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Printf("ReadCSVTable: read csv %v", err)
			return nil, err
		}
		var size = 0
		for n := 0; n < len(row); n++ {
			strings.TrimSpace(row[n])
			size += len(row[n])
		}
		if i == 0 {
			for j, s := range row {
				table.HeadNames[s] = int32(j)
			}
		} else {
			if size > 0 {
				table.Rows = append(table.Rows, row)
			}
		}
	}
	return table, nil
}

func ReadCSVFileToTable(filename string) (*GDTable, error) {
	data, err := os.ReadFile(filename)
	if err != nil {
		return nil, err
	}
	return ReadCSVTable(data)
}

func ParseBool(s string) bool {
	if len(s) == 0 {
		return false
	}
	switch s {
	case "y", "Y", "on", "ON", "yes", "YES":
		return true
	}
	b, _ := strconv.ParseBool(s)
	return b
}

func ParseI8(s string) int8 {
	var n = ParseI32(s)
	if n > math.MaxInt8 || n < math.MinInt8 {
		log.Printf("ParseI8: value %s out of range\n", s)
	}
	return int8(n)
}

func ParseU8(s string) uint8 {
	var n = ParseU32(s)
	if n > math.MaxUint8 || n < 0 {
		log.Printf("ParseU8: value %s out of range\n", s)
	}
	return uint8(n)
}

func ParseI16(s string) int16 {
	var n = ParseI32(s)
	if n > math.MaxInt16 || n < math.MinInt16 {
		log.Printf("ParseI16: value %s out of range\n", s)
	}
	return int16(n)
}

func ParseU16(s string) uint16 {
	var n = ParseU32(s)
	if n > math.MaxUint16 || n < 0 {
		log.Printf("ParseU16: value %s out of range\n", s)
	}
	return uint16(n)
}

func ParseI32(s string) int32 {
	if s == "" {
		return 0
	}
	n, err := strconv.ParseInt(s, 10, 32)
	if err != nil {
		log.Printf("ParseI32: cannot parse [%s] to int32: %v\n", s, err)
	}
	return int32(n)
}

func ParseU32(s string) uint32 {
	if s == "" {
		return 0
	}
	n, err := strconv.ParseUint(s, 10, 32)
	if err != nil {
		log.Printf("ParseU32: cannot parse [%s] to uint32: %v\n", s, err)
	}
	return uint32(n)
}

func ParseInt(s string) int {
	if s == "" {
		return 0
	}
	n, err := strconv.ParseInt(s, 10, 64)
	if err != nil {
		log.Printf("ParseInt: cannot parse [%s] to int: %v\n", s, err)
	}
	return int(n)
}

func ParseUint(s string) uint {
	if s == "" {
		return 0
	}
	n, err := strconv.ParseUint(s, 10, 64)
	if err != nil {
		log.Printf("ParseUint: cannot parse [%s] to int: %v\n", s, err)
	}
	return uint(n)
}

func ParseI64(s string) int64 {
	if s == "" {
		return 0
	}
	n, err := strconv.ParseInt(s, 10, 64)
	if err != nil {
		log.Printf("ParseI64: cannot parse [%s] to int64: %v\n", s, err)
	}
	return n
}

func ParseU64(s string) uint64 {
	if s == "" {
		return 0
	}
	n, err := strconv.ParseUint(s, 10, 64)
	if err != nil {
		log.Printf("ParseU64: cannot parse [%s] to uint64: %v\n", s, err)
	}
	return n
}

func ParseF32(s string) float32 {
	if s == "" {
		return 0
	}
	f, err := strconv.ParseFloat(s, 32)
	if err != nil {
		log.Printf("ParseF32: cannot parse [%s] to double: %v\n", s, err)
	}
	return float32(f)
}

func ParseF64(s string) float64 {
	if s == "" {
		return 0
	}
	f, err := strconv.ParseFloat(s, 64)
	if err != nil {
		log.Printf("ParseF64: cannot parse [%s] to double: %v\n", s, err)
	}
	return f
}

// ConvTo 泛型版本的字符串解析
// 使用方式`var a = ConvTo[int32](s)`，比具体类型的ParseXXX转换函数慢12%左右
func ConvTo[T cmp.Ordered | bool](s string) T {
	var zero T
	if s == "" {
		return zero
	}
	switch any(zero).(type) {
	case string:
		return any(s).(T)
	case bool:
		b := ParseBool(s)
		return any(b).(T)
	case int8:
		v := ParseI8(s)
		return any(v).(T)
	case uint8:
		v := ParseU8(s)
		return any(v).(T)
	case int16:
		v := ParseI16(s)
		return any(v).(T)
	case uint16:
		v := ParseU16(s)
		return any(v).(T)
	case int32:
		v := ParseI32(s)
		return any(v).(T)
	case uint32:
		v := ParseU32(s)
		return any(v).(T)
	case int:
		v := ParseInt(s)
		return any(v).(T)
	case uint:
		v := ParseUint(s)
		return any(v).(T)
	case int64:
		v := ParseI64(s)
		return any(v).(T)
	case uint64:
		v := ParseU64(s)
		return any(v).(T)
	case float32:
		v := ParseF32(s)
		return any(v).(T)
	case float64:
		v := ParseF64(s)
		return any(v).(T)
	}
	log.Printf("ConvTo: cannot parse [%s] to type %T\n", s, zero)
	return zero
}

// ParseSlice 解析字符串为slice, 格式如：a|b|c
func ParseSlice[T cmp.Ordered](text string, sep string) []T {
	var s = strings.TrimSpace(text)
	if s == "" {
		var zero []T
		return zero
	}
	var parts = strings.Split(text, sep)
	var ret = make([]T, 0, len(parts))
	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part != "" {
			val := ConvTo[T](part)
			ret = append(ret, val)
		}
	}
	return ret
}

// ParseMap 解析字符串为map，格式如：a:1|b:2|c:3
func ParseMap[K, V cmp.Ordered](text string, sep1, sep2 string) map[K]V {
	var ret = map[K]V{}
	var s = strings.TrimSpace(text)
	if s == "" {
		return ret
	}
	var parts = strings.Split(text, sep1)
	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part == "" {
			continue
		}
		pair := strings.Split(part, sep2)
		if len(pair) == 2 {
			key := ConvTo[K](pair[0])
			val := ConvTo[V](pair[1])
			ret[key] = val
		}
	}
	return ret
}
