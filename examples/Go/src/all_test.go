// Copyright (C) 2024 qi7chen@github. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

package config

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

var basePath, _ = filepath.Abs("../../datasheet/res")

func TestItemBoxAutogenCsvConfig(t *testing.T) {
	filename := filepath.Join(basePath, "item_box_define.csv")
	content, err := os.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}

	table, err := ReadCSVTable(content)
	if err != nil {
		t.Fatalf("%v", err)
	}
	for row := 0; row < table.RowSize(); row++ {
		var conf ItemBoxDefine
		if err := conf.ParseRow(table, row); err != nil {
			t.Fatalf("ParseRow: %v", err)
		}
		data, _ := json.Marshal(conf)
		t.Logf("%s\n", data)
	}
}

func TestItemBoxAutogenJsonConfig(t *testing.T) {
	filename := filepath.Join(basePath, "item_box_define.json")
	content, err := os.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var confList []ItemBoxDefine
	if err = json.Unmarshal(content, &confList); err != nil {
		t.Fatalf("JSON: %v", err)
	}
	for _, item := range confList {
		t.Logf("%v\n", item)
	}
}

func TestGlobalDefineAutogenCsvConfig(t *testing.T) {
	filename := filepath.Join(basePath, "global_define.csv")
	content, err := os.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	table, err := ReadCSVTable(content)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var conf GlobalDefine
	if err := conf.ParseFrom(table.ToKVMap()); err != nil {
		t.Fatalf("ParseFrom: %v", err)
	}
	t.Logf("%v\n", conf)
}

func TestGlobalDefineAutogenJsonConfig(t *testing.T) {
	filename := filepath.Join(basePath, "global_define.json")
	data, err := os.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var conf GlobalDefine
	if err := json.Unmarshal(data, &conf); err != nil {
		t.Fatalf("%v", err)
	}
	t.Logf("global define: %v", conf)
}

func TestNewbieGuideAutogenCsvConfig(t *testing.T) {
	filename := filepath.Join(basePath, "newbie_guide.csv")
	content, err := os.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	table, err := ReadCSVTable(content)
	if err != nil {
		t.Fatalf("%v", err)
	}
	for row := 0; row < table.RowSize(); row++ {
		var conf NewbieGuide
		if err := conf.ParseRow(table, row); err != nil {
			t.Fatalf("ParseRow: %v", err)
		}
		data, _ := json.Marshal(conf)
		t.Logf("%s\n", data)
	}
}

func TestNewbieGuideAutogenJsonConfig(t *testing.T) {
	filename := filepath.Join(basePath, "newbie_guide.json")
	data, err := os.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var cfgList []NewbieGuide
	if err = json.Unmarshal(data, &cfgList); err != nil {
		t.Fatalf("JSON: %v", err)
	}
	for _, cfg := range cfgList {
		t.Logf("%v\n", cfg)
	}
}

func TestSoldierAutogenCsvConfig(t *testing.T) {
	filename := filepath.Join(basePath, "soldier_define.csv")
	content, err := os.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	table, err := ReadCSVTable(content)
	if err != nil {
		t.Fatalf("%v", err)
	}
	for row := 0; row < table.RowSize(); row++ {
		var conf SoldierDefine
		if err := conf.ParseRow(table, row); err != nil {
			t.Fatalf("ParseRow: %v", err)
		}
		data, _ := json.Marshal(conf)
		t.Logf("%s\n", data)
	}
}

func TestSoldierAutogenJsonConfig(t *testing.T) {
	filename := filepath.Join(basePath, "soldier_define.json")
	data, err := os.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var cfgList []SoldierDefine
	if err = json.Unmarshal(data, &cfgList); err != nil {
		t.Fatalf("JSON Unmarshal: %v", err)
	}
	for _, cfg := range cfgList {
		t.Logf("%v\n", cfg)
	}
}
