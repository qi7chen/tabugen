package config

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	var pathPrefix = "../../res"
	var filename = fmt.Sprintf("%s/%s.json", pathPrefix, KeyGlobalPropertyDefineName)
	rawbytes, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}
	var confobj GlobalPropertyDefine
	if err = json.Unmarshal(rawbytes, &confobj); err != nil {
		t.Fatalf("%v", err)
	}
	t.Logf("%v", confobj)
}
