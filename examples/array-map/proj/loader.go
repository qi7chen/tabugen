package config

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
	"strings"
    
    "github.com/sirupsen/logrus"
)

var log = logrus.StandardLogger()

type DataSourceLoader interface {
	Init(string) error
	Close()
	LoadDataByKey(string) (*bytes.Buffer, error)
	LoadAll(...ConfigLoader) error
}

type ConfigLoader interface {
	LoadConfigData(DataSourceLoader) error
}

//从文件中读取配置
type FileLoader struct {
	path string
}

func NewFileLoader(filepath string) *FileLoader {
	return &FileLoader{
		path: filepath,
	}
}

func (l *FileLoader) Init(filepath string) error {
	l.path = filepath
	return nil
}

func (l *FileLoader) Close() {
	l.path = ""
	return
}

func (l *FileLoader) LoadDataByKey(key string) (*bytes.Buffer, error) {
	availableSuffix := []string{"_config.json", ".csv"}
	var filename = ""
	var err error
	for _, suffix := range availableSuffix {
		filename = fmt.Sprintf("%s/%s%s", l.path, key, suffix)
		if _, err = os.Stat(filename); err == nil {
			break
		} else {
			filename = ""
		}
	}
	if filename == "" {
		return nil, err
	}

	log.Infof("start load file %v", filename)
	rawbytes, err := ioutil.ReadFile(filename)
	if err != nil {
		return nil, err
	}
	var buf bytes.Buffer
	buf.Write(rawbytes)
	//log.Infof("Load config `%s` OK", key)
	return &buf, nil
}

func (l *FileLoader) LoadAll(loaders ...ConfigLoader) error {
	for _, loader := range loaders {
		if err := loader.LoadConfigData(l); err != nil {
			return err
		}
	}
	return nil
}

func parseBool(text string) bool {
	switch len(text) {
	case 0:
		return false
	case 1:
		return text[0] == '1'
	case 2:
		var value = strings.ToLower(text)
		return value == "on"
	case 3:
		var value = strings.ToLower(text)
		return value == "yes"
	case 4:
		var value = strings.ToLower(text)
		return value == "true"
	default:
		b, err := strconv.ParseBool(text)
		if err != nil {
			log.Panicf("%v, %v", text, err)
		}
		return b
	}
}

//
func MustParseTextValue(typename, valueText string, msgtips interface{}) interface{} {
	switch typename {
	case "bool":
		return parseBool(valueText)

	case "float32", "float64":
		f, err := strconv.ParseFloat(valueText, 64)
		if err != nil {
			log.Panicf("%s %s, %v, %v", typename, valueText, err, msgtips)
		}
		if typename == "float32" {
			return float32(f)
		}
		return f // float64

	case "uint", "uint8", "uint16", "uint32", "uint64":
		n, err := strconv.ParseUint(valueText, 10, 64)
		if err != nil {
			log.Panicf("%s %s, %v, %v", typename, valueText, err, msgtips)
		}
		if typename == "uint" {
			return uint(n)
		} else if typename == "uint8" {
			return uint8(n)
		} else if typename == "uint16" {
			return uint16(n)
		} else if typename == "uint32" {
			return uint32(n)
		}
		return n // uint64

	case "int", "int8", "int16", "int32", "int64":
		n, err := strconv.ParseInt(valueText, 10, 64)
		if err != nil {
			log.Panicf("%s %s, %v, %v", typename, valueText, err, msgtips)
		}
		if typename == "int" {
			return int(n)
		} else if typename == "int8" {
			return int8(n)
		} else if typename == "int16" {
			return int16(n)
		} else if typename == "int32" {
			return int32(n)
		}
		return n // int64

	default:
		return valueText
	}
}
