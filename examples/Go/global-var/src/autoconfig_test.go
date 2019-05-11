package config

import (
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	var loader = NewFileLoader("../res")
	defer loader.Close()

	global, err := LoadGlobalPropertyDefine(loader)
	if err != nil {
		t.Fatalf("%v", err)
	}
	t.Logf("global properties: %v", global)
}
