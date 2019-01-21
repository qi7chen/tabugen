package config

import (
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	var loader = NewFileLoader(".")
	defer loader.Close()
	DefaultLoader = loader

	conflist, err := LoadNewbieGuideDefineList()
	if err != nil {
		t.Fatalf("%v", err)
	}
	t.Logf("load %d config item", len(conflist))
}
