package config

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	var pathPrefix = "../../res"
	var filename = fmt.Sprintf("%s/%s.json", pathPrefix, KeySoldierPropertyDefineName)
	rawbytes, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var conflist []SoldierPropertyDefine
	if err = json.Unmarshal(rawbytes, &conflist); err != nil {
		t.Fatalf("%v", err)
	}
	for _, cfg := range conflist {
		t.Logf("%v\n", cfg)
	}
}
