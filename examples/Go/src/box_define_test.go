package config

import (
	"encoding/json"
	"io/ioutil"
	"testing"
)

func TestBoxAutogenCsvConfig(t *testing.T) {
	filename := "../../datasheet/res/box_probability_define.csv"
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}

	records, err := ReadCSVRecords(data)
	if err != nil {
		t.Fatalf("%v", err)
	}
	for _, rec := range records {
		var item BoxProbabilityDefine
		if err := item.ParseFrom(rec); err != nil {
			t.Fatalf("%v", err)
		}
		t.Logf("%v\n", item)
	}
}

func TestBoxAutogenJsonConfig(t *testing.T) {
	filename := "../../datasheet/res/box_probability_define.json"
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var cfgList []BoxProbabilityDefine
	if err = json.Unmarshal(data, &cfgList); err != nil {
		t.Fatalf("JSON: %v", err)
	}
	for _, item := range cfgList {
		t.Logf("%v\n", item)
	}

}
