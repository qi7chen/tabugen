package config

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	filename := fmt.Sprintf("../../res/%s.json", KeyNewbieGuideDefineName)
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var cfgList []NewbieGuideDefine
	if err = json.Unmarshal(data, &cfgList); err != nil {
		t.Fatalf("%v", err)
	}
	for _, cfg := range cfgList {
		t.Logf("%v\n", cfg)
	}
}
