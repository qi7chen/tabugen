package config

import (
	"fmt"
	"io/ioutil"
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	filename := "../../res/newbie_guide_define.csv"
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
