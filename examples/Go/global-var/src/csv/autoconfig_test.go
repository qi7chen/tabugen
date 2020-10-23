package config

import (
	"fmt"
	"io/ioutil"
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	filename := fmt.Sprintf("../../res/%s.csv", KeyGlobalPropertyDefineName)
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
