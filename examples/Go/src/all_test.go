package config

import (
    "testing"
)

func TestBoxAutogenCsvConfig(t *testing.T) {
    filename := "../../datasheet/res/box_probability_define.csv"
    data, err := os.ReadFile(filename)
    if err != nil {
        t.Fatalf("%v", err)
    }

    records, err := ReadCSVRecords(data)
    if err != nil {
        t.Fatalf("%v", err)
    }
    for _, rec := range records {
        var item BoxProbabilityDefine
        if err := item.ParseFrom(rec); err != nil {
            t.Fatalf("%v", err)
        }
        t.Logf("%v\n", item)
    }
}

func TestBoxAutogenJsonConfig(t *testing.T) {
    filename := "../../datasheet/res/box_probability_define.json"
    data, err := os.ReadFile(filename)
    if err != nil {
        t.Fatalf("%v", err)
    }
    var cfgList []BoxProbabilityDefine
    if err = json.Unmarshal(data, &cfgList); err != nil {
        t.Fatalf("JSON: %v", err)
    }
    for _, item := range cfgList {
        t.Logf("%v\n", item)
    }

}


func TestGlobalAutogenCsvConfig(t *testing.T) {
    var filename = "../../datasheet/res/global_property_define.csv"
    data, err := os.ReadFile(filename)
    if err != nil {
        t.Fatalf("%v", err)
    }
    records, err := ReadCSVRecords(data)
    if err != nil {
        t.Fatalf("%v", err)
    }
    var fields = RecordsToKVMap(records)
    var conf GlobalPropertyDefine
    conf.ParseFrom(fields)
    t.Logf("%v\n", conf)
}

func TestGlobalAutogenJsonConfig(t *testing.T) {
    filename := "../../datasheet/res/global_property_define.json"
    data, err := os.ReadFile(filename)
    if err != nil {
        t.Fatalf("%v", err)
    }
    var global GlobalPropertyDefine
    if err := json.Unmarshal(data, &global); err != nil {
        t.Fatalf("%v", err)
    }
    t.Logf("global properties: %v", global)
}


func TestGuideAutogenCsvConfig(t *testing.T) {
    filename := "../../datasheet/res/newbie_guide_define.csv"
    data, err := os.ReadFile(filename)
    if err != nil {
        t.Fatalf("%v", err)
    }
    records, err := ReadCSVRecords(data)
    if err != nil {
        t.Fatalf("%v", err)
    }
    for _, rec := range records {
        var item NewbieGuideDefine
        if err := item.ParseFrom(rec); err != nil {
            t.Fatalf("%v", err)
        }
        t.Logf("%v\n", item)
    }
}

func TestGuideAutogenJsonConfig(t *testing.T) {
    filename := "../../datasheet/res/newbie_guide_define.json"
    data, err := os.ReadFile(filename)
    if err != nil {
        t.Fatalf("%v", err)
    }
    var cfgList []NewbieGuideDefine
    if err = json.Unmarshal(data, &cfgList); err != nil {
        t.Fatalf("JSON: %v", err)
    }
    for _, cfg := range cfgList {
        t.Logf("%v\n", cfg)
    }
}


func TestSoldierAutogenCsvConfig(t *testing.T) {
    filename := "../../datasheet/res/soldier_property_define.csv"
    data, err := os.ReadFile(filename)
    if err != nil {
        t.Fatalf("%v", err)
    }

    records, err := ReadCSVRecords(data)
    if err != nil {
        t.Fatalf("%v", err)
    }
    for _, rec := range records {
        var item SoldierPropertyDefine
        if err := item.ParseFrom(rec); err != nil {
            t.Fatalf("%v", err)
        }
        t.Logf("%v\n", item)
    }
}

func TestSoldierAutogenJsonConfig(t *testing.T) {
    filename := "../../datasheet/res/soldier_property_define.json"
    data, err := os.ReadFile(filename)
    if err != nil {
        t.Fatalf("%v", err)
    }
    var cfgList []SoldierPropertyDefine
    if err = json.Unmarshal(data, &cfgList); err != nil {
        t.Fatalf("JSON: %v", err)
    }
    for _, cfg := range cfgList {
        t.Logf("%v\n", cfg)
    }
}
