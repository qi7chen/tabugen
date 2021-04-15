package config

import (
	"io/ioutil"
	"testing"
)

func TestAutogenConfig(t *testing.T) {
	filename := "../../res/soldier_property_define.csv"
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Fatalf("%v", err)
	}

	rows, err := ReadCSVRows(data)
	if err != nil {
		t.Fatalf("%v", err)
	}
	for _, row := range rows {
		var item SoldierPropertyDefine
		if err := item.ParseFromRow(row); err != nil {
			t.Fatalf("%v", err)
		}
		t.Logf("%v\n", item)
	}
}
