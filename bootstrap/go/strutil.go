package strutil

import (
	"log"
	"strconv"
)

//
func MustParseTextValue(typename, valueText string, msgtips interface{}) interface{} {
	switch typename {
	case "bool":
		b, err := strconv.ParseBool(valueText)
		if err != nil {
			log.Panicf("%s %s, %v, %v", typename, valueText, err, msgtips)
		}
		return b

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
