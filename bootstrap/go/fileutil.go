// Copyright © 2017 ichenq@outlook.com. All Rights Reserved.
//
// Any redistribution or reproduction of part or all of the contents in any form
// is prohibited.
//
// You may not, except with our express written permission, distribute or commercially
// exploit the content. Nor may you transmit it or store it in any other website or
// other form of electronic retrieval system.

package fileutil

import (
	"bytes"
	"compress/zlib"
	"database/sql"
	"encoding/base64"
	"fmt"
	"io/ioutil"
	"os"
	"strings"

	log "github.com/sirupsen/logrus"
)

type ConfigLoader interface {
	LoadConfigData(DataSourceLoader) error
}

type DataSourceLoader interface {
	Init(string) error
	Close()
	LoadDataByKey(string) (*bytes.Buffer, error)
	LoadAll(...ConfigLoader) error
}

//数据库配置读取
type SQLLoader struct {
	db *sql.DB
}

func NewSQLLoader(db *sql.DB) *SQLLoader {
	return &SQLLoader{
		db: db,
	}
}

func (l *SQLLoader) Init(dsn string) error {
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		return err
	}
	err = db.Ping()
	if err != nil {
		return err
	}
	l.db = db
	return nil
}

func (l *SQLLoader) Close() {
	if l.db != nil {
		l.db.Close()
	}
	l.db = nil
}

//根据key读取数据
func (l *SQLLoader) LoadDataByKey(key string) (*bytes.Buffer, error) {
	var typetext, content string
	stmt := fmt.Sprintf("SELECT `type`, `text` FROM `config` WHERE `name`='%s'", key)
	if err := l.db.QueryRow(stmt).Scan(&typetext, &content); err != nil {
		log.Errorf("LoadDataByKey: QueryRow, [%s], %v", stmt, err)
		return nil, err
	}
	var buf bytes.Buffer
	var typelist = strings.Split(typetext, "-")
	if len(typelist) > 1 && typelist[1] == "deflate" {
		data, err := base64.StdEncoding.DecodeString(content)
		if err != nil {
			log.Errorf("LoadDataByKey:base64 decode, [%s], %v", stmt, err)
			return nil, err
		}
		reader, err := zlib.NewReader(bytes.NewReader(data))
		if err != nil {
			log.Errorf("LoadDataByKey: zlib inflate, [%s], %v", stmt, err)
			return nil, err
		}
		var b bytes.Buffer
		if _, err := b.ReadFrom(reader); err != nil {
			log.Errorf("LoadDataByKey: read buffer, [%s], %v", stmt, err)
			return nil, err
		}
		buf = b
	} else {
		buf.WriteString(content)
	}
	//log.Infof("Load config `%s` OK", key)
	return &buf, nil
}

func (l *SQLLoader) LoadAll(loaders ...ConfigLoader) error {
	for _, loader := range loaders {
		if err := loader.LoadConfigData(l); err != nil {
			return err
		}
	}
	return nil
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
