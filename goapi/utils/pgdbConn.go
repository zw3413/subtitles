package utils

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	_ "github.com/lib/pq"
	"gopkg.in/ini.v1"
)

var db *sql.DB

func init() {
	ConnPgDB()
}

func ConnPgDB() {
	cfg, err := ini.Load("./config.ini")
	if err != nil {
		fmt.Printf("Fail to read file: %v", err)
		os.Exit(1)
	}
	user := cfg.Section("db").Key("user").String()
	password := cfg.Section("db").Key("password").String()
	dbname := cfg.Section("db").Key("dbname").String()
	host := cfg.Section("db").Key("host").String()
	port := cfg.Section("db").Key("port").String()
	connStr := fmt.Sprintf("user=%v password=%v host=%v port=%v dbname =%v sslmode=disable ", user, password, host, port, dbname)

	database, err := sql.Open("postgres", connStr)

	if err != nil {
		log.Fatal(err)
		db = nil
		return
	}
	db = database
}

func scanRow(rows *sql.Rows) (map[string]interface{}, error) {
	columns, _ := rows.Columns()

	vals := make([]interface{}, len(columns))
	valsPtr := make([]interface{}, len(columns))

	for i := range vals {
		valsPtr[i] = &vals[i]
	}

	err := rows.Scan(valsPtr...)
	if err != nil {
		return nil, err
	}

	r := make(map[string]interface{})

	for i, v := range columns {
		if va, ok := vals[i].([]byte); ok {
			r[v] = string(va)
		} else {
			r[v] = vals[i]
		}
	}
	return r, nil
}

func GetAllData(sql string, args ...interface{}) ([]map[string]interface{}, error) {
	rows, err := db.Query(sql, args...)
	if err != nil {
		return nil, err
	}
	defer func() {
		rows.Close()
		if r := recover(); r != nil {
			log.Println("Recovered from ", r)
			return
		}
	}()
	result := make([]map[string]interface{}, 0)

	for rows.Next() {
		row, err := scanRow(rows)
		if err != nil {
			return nil, err
		}
		result = append(result, row)
	}
	return result, nil
}

func ExecUpdate(sql string, args ...interface{}) error {
	stmt, err := db.Prepare(sql)
	if err != nil {
		log.Fatal(err)
		return err
	}
	defer stmt.Close()
	res, err := stmt.Exec(args...)
	if err != nil {
		log.Fatal(err)
		return err
	}
	rownum, err := res.RowsAffected()
	if err != nil || rownum == 0 {
		log.Fatal(err)
		return err
	}
	return nil
}
