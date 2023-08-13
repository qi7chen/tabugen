package config

import (
	"encoding/json"
	"os"
	"testing"
)

func TestGuideAutogenCsvConfig(t *testing.T) {
	filename := "../../datasheet/res/newbie_guide_define.csv"
	data, err := os.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	records, err := ReadCSVRecords(data)
	if err != nil {
		t.Fatalf("%v", err)
	}
	for _, rec := range records {
		var item NewbieGuideDefine
		if err := item.ParseFrom(rec); err != nil {
			t.Fatalf("%v", err)
		}
		t.Logf("%v\n", item)
	}
}

func TestGuideAutogenJsonConfig(t *testing.T) {
	filename := "../../datasheet/res/newbie_guide_define.json"
	data, err := os.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var cfgList []NewbieGuideDefine
	if err = json.Unmarshal(data, &cfgList); err != nil {
		t.Fatalf("JSON: %v", err)
	}
	for _, cfg := range cfgList {
		t.Logf("%v\n", cfg)
	}
}
