package config

import (
	"encoding/json"
	"io/ioutil"
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	filename := "../../res/box_probability_define.json"
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
