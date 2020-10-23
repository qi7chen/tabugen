package config

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	filename := fmt.Sprintf("../../res/%s.json", KeyBoxProbabilityDefineName)
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var cfgList []BoxProbabilityDefine
	if err = json.Unmarshal(data, &cfgList); err != nil {
		t.Fatalf("JSON: %v", err)
	}
	for _, item := range cfgList {
		fmt.Printf("%v\n", item)
	}

}
