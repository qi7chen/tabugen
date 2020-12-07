package config

import (
	"io/ioutil"
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	filename := "../../res/global_property_define.csv"
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}

	global, err := LoadGlobalPropertyDefine(data)
	if err != nil {
		t.Fatalf("%v", err)
	}
	t.Logf("global properties: %v", global)
}
