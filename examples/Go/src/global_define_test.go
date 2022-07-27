package config

import (
	"encoding/json"
	"io/ioutil"
	"testing"
)

func TestGlobalAutogenCsvConfig(t *testing.T) {
	var filename = "../../datasheet/res/global_property_define.csv"
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	records, err := ReadCSVRecords(data)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var fields = RecordsToKVMap(records)
	var conf GlobalPropertyDefine
	conf.ParseFields(fields)
	t.Logf("%v\n", conf)
}

func TestGlobalAutogenJsonConfig(t *testing.T) {
	filename := "../../datasheet/res/global_property_define.json"
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var global GlobalPropertyDefine
	if err := json.Unmarshal(data, &global); err != nil {
		t.Fatalf("%v", err)
	}
	t.Logf("global properties: %v", global)
}
