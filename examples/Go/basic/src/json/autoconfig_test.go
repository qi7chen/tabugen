package config

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	filename := fmt.Sprintf("../../res/%s.csv", KeySoldierPropertyDefineName)
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var cfgList []SoldierPropertyDefine
	if err = json.Unmarshal(data, &cfgList); err != nil {
		t.Fatalf("JSON: %v", err)
	}
	for _, cfg := range conflist {
		t.Logf("%v\n", cfg)
	}
}
