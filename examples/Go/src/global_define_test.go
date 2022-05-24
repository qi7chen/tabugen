package config

import (
	"encoding/json"
	"io/ioutil"
	"testing"
)

func TestGlobalAutogenCsvConfig(t *testing.T) {
	filename := "../res/global_property_define.json"
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var conf GlobalPropertyDefine
	if err = json.Unmarshal(data, &conf); err != nil {
		t.Fatalf("JSON: %v", err)
	}
	t.Logf("%v\n", conf)
}

func TestGlobalAutogenJsonConfig(t *testing.T) {
	filename := "../res/global_property_define.csv"
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var global GlobalPropertyDefine
	if err := global.Unmarshal(data); err != nil {
		t.Fatalf("%v", err)
	}
	t.Logf("global properties: %v", global)
}
