package config

import (
	"testing"
	"io/ioutil"
	"fmt"
)

func TestAutogenConfig(t *testing.T) {
	filename := fmt.Sprintf("../../res/%s.csv", KeyNewbieGuideDefineName)
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	cfgList, err := LoadNewbieGuideDefineList(data)
	if err != nil {
		t.Fatalf("%v", err)
	}
	for _, cfg := range cfgList {
		fmt.Printf("%v\n", cfg)
	}
}
