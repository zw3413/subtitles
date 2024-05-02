package utils

import (
	"context"
	"errors"
	"fmt"
	"goapi/src/configs"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
	log "github.com/jeanphorn/log4go"
)

var (
	ts_dbhost      string
	ts_dbport      int
	ts_dbname      string
	ts_username    string
	ts_passwd      string
	ts_maxopenconn int
	ts_dbPool      *pgxpool.Pool
	ts_batchNum    int
	//定時器 自動寫入的20200820
	ts_autoWriterTimer *time.Timer
	//最後一次寫入時間20200820
	ts_lastWriteOn time.Time = time.Now()
	ts_policyHour  int
	logwrite       string
	lastWriteOn    time.Time = time.Now()
)
var fieldsValues = struct {
	sync.RWMutex
	fields []TsEntityObj
	tables []string
}{fields: make([]TsEntityObj, 0),
	tables: make([]string, 0)}

func init() {
	iniConfig := new(configs.Config)
	iniConfig.InitConfig()

	logwrite = iniConfig.Read("influxdb", "logwrite")
	UseTimeScaleDbPool()
}

// ok的时候是否写influxab    Y:写入  N:不写入
func Iswritetsdb() string {
	if len(logwrite) == 0 {
		return "Y"
	} else {
		return logwrite
	}
}

func InfluxLogDataNew(tablename string, keycode string, cstime string, path string, funcname string, requestid string, executeFlag string,
	requestParam string, responseParam string, clientIp string, hostIp, responseMsg string, starttime string, useremail string, subscribed bool, inlimit bool) {
	defer func() {
		if err := recover(); err != nil {
			errLog := fmt.Sprintf("send2Influx  panic: %v", err)
			log.LOGGER("SUBX").Error(errLog)
		}
	}()
	ts_model := TsEntityObj{}
	request_date, err := time.Parse(starttime, "20060102150405")
	if err != nil {
		ts_model.Requestdate = time.Now()
	} else {
		ts_model.Requestdate = request_date
	}
	ts_model.Keycode = keycode
	ts_model.Time = ts_model.Requestdate
	ts_model.Servicename = funcname
	ts_model.Requestpath = path
	ts_model.Requestid = requestid
	ts_model.Requestparam = requestParam
	ts_model.Clientip = clientIp
	ts_model.Hostip = hostIp
	ts_model.Responsedate = time.Now()
	costimeint64, _ := strconv.ParseInt(cstime, 10, 64)
	ts_model.Costtime = costimeint64 // time.Since(ts_model.Responsedate).Milliseconds()
	//ts_model.Costtime = time.Since(ts_model.Requestdate).Milliseconds()
	ts_model.Responseparam = responseParam
	ts_model.Returnmessage = responseMsg
	ts_model.Executeflag = executeFlag
	ts_model.Usereamil = useremail

	if subscribed {
		ts_model.subscribed = "Y"
	} else {
		ts_model.subscribed = "N"
	}

	if inlimit {
		ts_model.inlimit = "Y"
	} else {
		ts_model.inlimit = "N"
	}

	// 同时写入 timescaledb
	//HACK:: 请求的时间和返回的时间 处理存在问题
	TsWrite(tablename, ts_model)
}

// TsWrite 向 timescaledb 表中写入数据 fields 栏位和对应的值
func TsWrite(tablename string, tsData TsEntityObj) {
	// timescale db 超表名称中不能存在'.'并且大小写也有限制
	tablename = strings.Replace(tablename, "\"", "_", -1)
	tablename = strings.Replace(tablename, ".", "_", -1)
	tablename = strings.Replace(tablename, "'", "_", -1)
	tablename = strings.Replace(tablename, "-", "_", -1)
	tablename = strings.ToLower(tablename)
	isOk, _ := createTableIfNotExists(tablename)
	if !isOk {
		//不存在也无法创建时返回
		return
	}
	fieldsValues.Lock()
	fieldsValues.tables = append(fieldsValues.tables, tablename)
	fieldsValues.fields = append(fieldsValues.fields, tsData)
	currSliceLen := len(fieldsValues.fields)
	//消費
	if currSliceLen > ts_batchNum {
		//最後一次訪問時間
		lastWriteOn = time.Now()
		//fmt.Printf("最后一次访问时间:%v", lastWriteOn)
		if nil == ts_dbPool {
			UseTimeScaleDbPool()
		}
		// 两次判断dbpool是否为空 不为空时执行,为nil时 清空slice
		if ts_dbPool != nil {
			// insterTimeseriesData := `insert into "/checkconfig/manualrefresh" ("time", "keycode", "servicename", "requestdate", "requestpath", "requestid", "requestparam",
			//  "clientip", "equipmentip", "responsedate", "costtime", "responseparam", "returncode", "returnmessage", "executeflag", "hashcode")
			//  values ('2022-06-13 19:38:24.531322', '3', '3', '2022-06-13 19:38:24.531322', null, null, null, null, null, '2022-06-13 19:38:24.531322', null, null, null, null, null, null),
			// 	('2022-06-13 19:38:24.531322', '3', '3', '2022-06-13 19:38:24.531322', null, null, null, null, null, '2022-06-13 19:38:24.531322', null, null, null, null, null, null); `
			insterTimeseriesData := `insert into "%s" ("time", "keycode", "servicename", "requestdate", "requestpath", "requestid" ,"requestparam",
		 "clientip", "hostip", "responsedate", "costtime", "responseparam", "returncode", "returnmessage", "executeflag", "hashcode","useremail","subscribed","inlimit") 
		 values ($1, $2, $3,$4, $5, $6, $7, $8, $9,$10, $11, $12, $13, $14, $15, $16, $17, $18, $19)`

			// batch 批写入
			batch := &pgx.Batch{}
			for i := range fieldsValues.fields {
				var insertData = fieldsValues.fields[i]
				if insertData.Time.IsZero() {
					insertData.Time = insertData.Requestdate
				}
				// 写入队列
				batch.Queue(fmt.Sprintf(insterTimeseriesData, fieldsValues.tables[i]),
					insertData.Time, insertData.Keycode, insertData.Servicename, insertData.Requestdate, insertData.Requestpath, insertData.Requestid, insertData.Requestparam,
					insertData.Clientip, insertData.Hostip, insertData.Responsedate, insertData.Costtime, insertData.Responseparam, insertData.Returncode, insertData.Returnmessage, insertData.Executeflag, insertData.Hashcode, insertData.Usereamil, insertData.subscribed, insertData.inlimit)
			}

			br := ts_dbPool.SendBatch(context.Background(), batch)
			// 执行
			_, err := br.Exec()
			if err != nil {
				log.LOGGER("SUBX").Error(fmt.Sprintf("bath insert error:%v", err))
			} else {
				//log.LOGGER("SUBX").Info(fmt.Sprintf("bath insert %v ok", currSliceLen))
			}
			// 关闭
			br.Close()
		}
		// 执行完成后清空 slice (不管ts_dbpool是否为nil)
		fieldsValues.fields = make([]TsEntityObj, 0)
		fieldsValues.tables = make([]string, 0)
	}
	fieldsValues.Unlock()
	//fmt.Printf("时间到了%v\n", time.Now().Sub(lastWriteOn))
	//最後一次訪問時間和當前時間的差 大於等於 60秒時 每個60秒執行一次寫入動作
	// if time.Duration(time.Since(lastWriteOn).Seconds()) >= time.Second*60 {
	// 	//	fmt.Printf("每60秒执行一次:%v\n", lastWriteOn)
	// 	ts_autoWriterAfterTime()
	// }
	// if time.Now().Sub(lastWriteOn) >= time.Second*60 {
	// 	//	fmt.Printf("每60秒执行一次:%v\n", ts_lastWriteOn)
	// 	ts_autoWriterAfterTime()
	// }
}

// createTableIfNotExists 如果表不存在则创建表
func createTableIfNotExists(tablename string) (bool, error) {
	tablename = strings.Replace(tablename, "\"", "_", -1)
	tablename = strings.Replace(tablename, ".", "_", -1)
	tablename = strings.Replace(tablename, "'", "_", -1)
	tablename = strings.Replace(tablename, "-", "_", -1)
	tablename = strings.ToLower(tablename)

	queryCreateTableIfNotExists := `CREATE TABLE "timescale_hypertable_template" (
  "time" timestamp(6) DEFAULT now(),
  "keycode" text COLLATE "pg_catalog"."default",
  "servicename" text COLLATE "pg_catalog"."default",
  "requestdate" timestamp(6) DEFAULT now(),
  "requestpath" text COLLATE "pg_catalog"."default",
  "requestid" text COLLATE "pg_catalog"."default",
  "requestparam" text COLLATE "pg_catalog"."default",
  "clientip" text COLLATE "pg_catalog"."default",
  "hostip" text COLLATE "pg_catalog"."default",
  "responsedate" timestamp(6) DEFAULT now(),
  "costtime" int8,
  "responseparam" text COLLATE "pg_catalog"."default",
  "returncode" text COLLATE "pg_catalog"."default",
  "returnmessage" text COLLATE "pg_catalog"."default",
  "executeflag" text COLLATE "pg_catalog"."default",
  "hashcode" text COLLATE "pg_catalog"."default",
  "useremail" text COLLATE "pg_catalog"."default",
  "subscribed" text COLLATE "pg_catalog"."default",
  "inlimit" text COLLATE "pg_catalog"."default"
  )
  ;
  COMMENT ON COLUMN "timescale_hypertable_template"."time" IS '超表需要的time';
  COMMENT ON COLUMN "timescale_hypertable_template"."keycode" IS '关键信息';
  COMMENT ON COLUMN "timescale_hypertable_template"."servicename" IS '服务名称/function名称';
  COMMENT ON COLUMN "timescale_hypertable_template"."requestdate" IS '请求的时间';
  COMMENT ON COLUMN "timescale_hypertable_template"."requestpath" IS '请求url路径';
  COMMENT ON COLUMN "timescale_hypertable_template"."requestid" IS '请求的requestid';
  COMMENT ON COLUMN "timescale_hypertable_template"."requestparam" IS '请求的参数';
  COMMENT ON COLUMN "timescale_hypertable_template"."clientip" IS '客户端的ip';
  COMMENT ON COLUMN "timescale_hypertable_template"."responsedate" IS '处理完成时间';
  COMMENT ON COLUMN "timescale_hypertable_template"."costtime" IS '处理执行的实际';
  COMMENT ON COLUMN "timescale_hypertable_template"."responseparam" IS '返回的参数';
  COMMENT ON COLUMN "timescale_hypertable_template"."returncode" IS '返回错误代码';
  COMMENT ON COLUMN "timescale_hypertable_template"."returnmessage" IS '返回的消息';
  COMMENT ON COLUMN "timescale_hypertable_template"."executeflag" IS '执行状态 Y执行成功,N执行失败';
  COMMENT ON COLUMN "timescale_hypertable_template"."hashcode" IS 'hashcode';
  COMMENT ON COLUMN "timescale_hypertable_template"."useremail" IS '用户邮箱地址';
  COMMENT ON TABLE "timescale_hypertable_template" IS 'api中日志记录使用的timescaledb的表 需要使用 create_hypertable创建超表';
  select create_hypertable('timescale_hypertable_template','time', chunk_time_interval => INTERVAL '1 day');
	`
	queryCreateTableIfNotExists = strings.Replace(queryCreateTableIfNotExists, "timescale_hypertable_template", tablename, -1)
	//fmt.Println(queryCreateTableIfNotExists)
	if ts_dbPool == nil {
		return false, errors.New("pool is nil")
	}
	var i_tablecount int64
	//select count(*) from pg_class where relname ='sfc_b_pvd_scanner' ;
	//select count(*) from pg_tables where  tablename='tcuser';
	err := ts_dbPool.QueryRow(context.Background(), "select count(*) from pg_tables where  tablename = $1", tablename).Scan(&i_tablecount)
	if err != nil {
		log.LOGGER("SUBX").Error(fmt.Sprintf("query table %s error:%v", tablename, err))
		return false, err
	}
	if i_tablecount <= 0 {
		_, err = ts_dbPool.Exec(context.Background(), queryCreateTableIfNotExists)
		if err != nil {
			log.LOGGER("SUBX").Error(fmt.Sprintf("create hypertable table %s error:%v", tablename, err))
			return false, err
		}

		var i_jobcount int64
		//新建表后建保留策略 默認保留 7天
		err = ts_dbPool.QueryRow(context.Background(), "select count(*) from timescaledb_information.jobs where hypertable_name=$1", tablename).Scan(&i_jobcount)
		if err != nil {
			log.LOGGER("SUBX").Error(fmt.Sprintf("query jobs table %s error:%v", tablename, err))
			return false, err
		}
		if i_jobcount <= 0 {
			if ts_policyHour <= 0 {
				ts_policyHour = 168
			}
			add_policy := "SELECT add_retention_policy('" + tablename + "', INTERVAL '" + strconv.Itoa(ts_policyHour) + " hours');"
			_, err = ts_dbPool.Exec(context.Background(), add_policy)
			if err != nil {
				log.LOGGER("SUBX").Error(fmt.Sprintf("add_retention_policy table %s error:%v", tablename, err))
				return false, err
			}

		}
	}

	// 表存在是返回 true
	return true, nil
}
func UseTimeScaleDbPool() {
	iniConfig := new(configs.Config)
	iniConfig.InitConfig()
	ts_policyHour, _ = strconv.Atoi(iniConfig.Read("timescaledb", "ts_policyhour"))
	ts_dbhost = iniConfig.Read("timescaledb", "ts_dbhost")
	ts_dbport, _ = strconv.Atoi(iniConfig.Read("timescaledb", "ts_dbport"))
	ts_dbname = iniConfig.Read("timescaledb", "ts_dbname")
	ts_username = iniConfig.Read("timescaledb", "ts_username")
	ts_passwd = iniConfig.Read("timescaledb", "ts_passwd")
	ts_connInfo := fmt.Sprintf("postgres://%s:%s@%s:%d/%s", ts_username, ts_passwd, ts_dbhost, ts_dbport, ts_dbname)
	log.LOGGER("SUBX").Info(ts_connInfo)
	ts_databasePool, err := pgxpool.Connect(context.Background(), ts_connInfo)
	//database.SetConnMaxLifetime(10 * time.Second)
	ts_maxopenconn, _ = strconv.Atoi(iniConfig.Read("timescaledb", "ts_maxopenconn"))
	ts_databasePool.Config().MaxConns = int32(ts_maxopenconn)
	ts_batchNum, _ = strconv.Atoi(iniConfig.Read("timescaledb", "ts_batchnum"))
	if err != nil {
		fmt.Println("connect timescaledb failed!")
		ts_databasePool = nil
		return
	}
	ts_dbPool = ts_databasePool
}

// TsEntityObj timescaledb 写入时的结构体
type TsEntityObj struct {
	Time          time.Time
	Keycode       string
	Servicename   string
	Requestdate   time.Time
	Requestpath   string
	Requestid     string
	Requestparam  string
	Clientip      string
	Hostip        string
	Responsedate  time.Time
	Costtime      int64
	Responseparam string
	Returncode    string
	Returnmessage string
	Executeflag   string
	Hashcode      string
	Usereamil     string
	subscribed    string
	inlimit       string
}
