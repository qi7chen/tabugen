package config

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	filename := fmt.Sprintf("../../res/%s.json", KeySoldierPropertyDefineName)
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var conflist []SoldierPropertyDefine
	if err = json.Unmarshal(data, &conflist); err != nil {
		t.Fatalf("%v", err)
	}
	for _, cfg := range conflist {
		t.Logf("%v\n", cfg)
	}
}
