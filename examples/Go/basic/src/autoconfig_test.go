package config

import (
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	var loader = NewFileLoader("../res")
	defer loader.Close()

	conflist, err := LoadSoldierPropertyDefineList(loader)
	if err != nil {
		t.Fatalf("%v", err)
	}
	for _, cfg := range conflist {
		t.Logf("%v\n", cfg)
	}
}
