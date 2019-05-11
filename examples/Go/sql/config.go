// This file is auto-generated by taxi v0.3.3. DO NOT EDIT!

package orm

import (
	"database/sql"
	"fatchoy/storage"
)

//
type Player struct {
	Id    int32  `json:"id"`    //
	Name  string `json:"name"`  //
	Level uint32 `json:"level"` //
}

func (m *Player) SetId(v int32) {
	m.Id = v
}
func (m *Player) SetName(v string) {
	m.Name = v
}
func (m *Player) SetLevel(v uint32) {
	m.Level = v
}

const SqlPlayerStmt = "SELECT `id`, `name`, `level` FROM `player`"

func (p *Player) Load(rows *sql.Rows) error {
	return rows.Scan(&p.Id, &p.Name, &p.Level)
}

func (p *Player) InsertStmt() *storage.DBOperation {
	return storage.NewDBOperation("INSERT INTO `player`(`id`, `name`, `level`) VALUES(?, ?, ?)", p.Id, p.Name, p.Level)
}

func (p *Player) UpdateStmt() *storage.DBOperation {
	return storage.NewDBOperation("UPDATE `player` SET `name`=?, `level`=? WHERE `id`=?", p.Name, p.Level, p.Id)
}

func (p *Player) DeleteStmt() *storage.DBOperation {
	return storage.NewDBOperation("DELETE FROM `player` WHERE `id`=?", p.Id)
}