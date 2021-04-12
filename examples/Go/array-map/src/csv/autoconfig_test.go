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
	rows, err := ReadCSVRows(data)
	if err != nil {
		t.Fatalf("%v", err)
	}
	for _, row := range rows {
	    var item NewbieGuideDefine
	    if err := item.ParseFromRow(row); err != nil {
	        t.Fatalf("%v", err)
	    }
		fmt.Printf("%v\n", item)
	}
}
