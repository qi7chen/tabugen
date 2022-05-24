package config

import (
	"encoding/json"
	"io/ioutil"
	"testing"
)

func TestGuideAutogenCsvConfig(t *testing.T) {
	filename := "../res/newbie_guide_define.csv"
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	rows, err := ReadCSVRows(data)
	if err != nil {
		t.Fatalf("%v", err)
	}
	for _, row := range rows {
		var item NewbieGuideDefine
		if err := item.ParseFromRow(row); err != nil {
			t.Fatalf("%v", err)
		}
		t.Logf("%v\n", item)
	}
}

func TestGuideAutogenJsonConfig(t *testing.T) {
	filename := "../res/newbie_guide_define.json"
	data, err := ioutil.ReadFile(filename)
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
