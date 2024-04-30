package utils

import (
	"database/sql"
	"fmt"
	"goapi/src/configs"
	"log"
	"strconv"

	_ "github.com/lib/pq"
)

var (
	dbhost      string
	dbport      int
	dbname      string
	username    string
	passwd      string
	maxopenconn int
	maxidleConn int
	db          *sql.DB
)

func init() {
	ConnPgDB()
}

func ConnPgDB() {
	iniConfig := new(configs.Config)
	iniConfig.InitConfig()
	dbhost = iniConfig.Read("pg", "dbhost")
	dbport, _ = strconv.Atoi(iniConfig.Read("pg", "dbport"))
	dbname = iniConfig.Read("pg", "dbname")
	username = iniConfig.Read("pg", "username")
	passwd = iniConfig.Read("pg", "passwd")
	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
		dbhost, dbport, username, passwd, dbname)

	database, err := sql.Open("postgres", psqlInfo)
	maxopenconn, _ = strconv.Atoi(iniConfig.Read("pg", "maxopenconn"))
	maxidleConn, _ = strconv.Atoi(iniConfig.Read("pg", "maxidleConn"))
	database.SetMaxOpenConns(maxopenconn)
	database.SetMaxIdleConns(maxidleConn)

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
