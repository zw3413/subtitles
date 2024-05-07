package wheel

import (
	"encoding/json"
	"fmt"
	"goapi/src/utils"
	"io"
	"net/http"
	"strconv"
	"time"

	"github.com/buger/jsonparser"
	"github.com/gin-gonic/gin"
	log "github.com/jeanphorn/log4go"
	uuid "github.com/satori/go.uuid"
)

/**
這是一個輪子，可以滾得很遠很遠……
H2103424
20220317
*/

type responseInfo struct {
	Rc          string `json:"rc"`
	Rm          string `json:"rm"`
	RequestUuid string `json:"request_id"`
	CostTime    string `json:"costtime"`
	//Data        []map[string]interface{} `json:"data"`
	Data string `json:"data"`
}
type requestScrapScan struct {
	Hashcode  string   `json:"hashcode"`
	RequestID string   `json:"request_id"`
	DeviceIp  string   `json:"device_ip"`
	Function  string   `json:"function"`
	Uuid      string   `json:"uuid"`
	Params    []string `json:"params"`
}

/*
*
 */
func AllPurpose(c *gin.Context) {
	executeFlag := "Y"
	var responseInfo responseInfo
	var requestInfo requestScrapScan
	startTime := time.Now()
	startTimeStr := startTime.Format("20060102150405")

	//讀取傳參
	reqBody, reqErr := io.ReadAll(c.Request.Body)

	//日誌記錄及異常處理
	defer func() {
		costtime := (time.Now().UnixNano() - startTime.UnixNano()) / 1000000
		responseInfo.CostTime = strconv.FormatInt(costtime, 10)
		if err := recover(); err != nil {
			executeFlag = "N"
			errLog := fmt.Sprintf("[wheel.AllPurpose] defer error:%v", err)
			log.LOGGER("SUBX").Error(errLog)
			responseInfo.Rc = "999"
			responseInfo.Rm = "系統異常，" + errLog
		}
		jsonStr, _ := json.Marshal(responseInfo)
		if executeFlag == "N" || utils.Iswritetsdb() == "Y" {
			go utils.InfluxLogDataNew("wheel.AllPurpose", "", strconv.FormatInt(costtime, 10), c.Request.RequestURI,
				requestInfo.Function, requestInfo.RequestID, executeFlag, string(reqBody), string(jsonStr), c.RemoteIP(), "", "", startTimeStr, "", false, false)
		}
		c.JSON(http.StatusOK, responseInfo)
	}()

	if reqErr != nil || reqBody == nil {
		executeFlag = "N"
		responseInfo.Rc = "5910"
		responseInfo.Rm = "傳參解析異常"
		return
	}
	if len(reqBody) == 0 {
		executeFlag = "N"
		responseInfo.Rc = "5911"
		responseInfo.Rm = "傳參不能為空"
		return
	}
	// 非空欄位驗證
	notNullFields := []string{"function", "params"}
	for _, field := range notNullFields {
		fieldvalue, fieldErr := jsonparser.GetUnsafeString(reqBody, field)
		if fieldErr != nil {
			responseInfo.Rc = "5913"
			responseInfo.Rm = field + "參數轉換異常"
			executeFlag = "N"
			return
		} else if len(fieldvalue) == 0 {
			responseInfo.Rc = "5914"
			responseInfo.Rm = field + "參數不能為空"
			executeFlag = "N"
			return
		}
	}
	//轉換JSON
	err := json.Unmarshal(reqBody, &requestInfo)
	if err != nil {
		executeFlag = "N"
		responseInfo.Rc = "5912"
		responseInfo.Rm = "JSON轉換異常"
		return
	}
	if len(requestInfo.RequestID) > 0 {
		responseInfo.RequestUuid = requestInfo.RequestID
	} else {
		responseInfo.RequestUuid = uuid.NewV4().String()
	}

	//調用存儲過程
	sqlStr := "select * from " + requestInfo.Function + "("
	inParams := make([]interface{}, 0)
	paramsCount := 1
	for _, param := range requestInfo.Params {
		sqlStr += "$" + strconv.Itoa(paramsCount) + ","
		inParams = append(inParams, param)
		paramsCount++
	}
	sqlStr = string([]rune(sqlStr)[:len(sqlStr)-1]) + ")"

	rows, err := utils.GetAllData(sqlStr, inParams...)
	if err != nil {
		executeFlag = "N"
		errInfo := fmt.Sprintf("[wheel.AllPurpose] Func SQL execute error:%v", err)
		responseInfo.Rc = "5001"
		responseInfo.Rm = errInfo
		log.LOGGER("SUBX").Error(errInfo)
		return
	}
	responseInfo.Rc = "000"
	responseInfo.Rm = "OK"

	val, ok := rows[0]["o_resultcode"]
	if ok && val != nil {
		responseInfo.Rc = val.(string)
	}
	val, ok = rows[0]["o_resultmsg"]
	if ok && val != nil {
		responseInfo.Rm = val.(string)
	}
	val, ok = rows[0]["o_data"]
	if ok && val != nil {
		responseInfo.Data = val.(string)
	}
}

// 带有校验的方法
func AllPurpose_external(c *gin.Context) {
	executeFlag := "Y"
	var responseInfo responseInfo
	var requestInfo requestScrapScan
	startTime := time.Now()
	startTimeStr := startTime.Format("20060102150405")

	//讀取傳參
	reqBody, reqErr := io.ReadAll(c.Request.Body)

	//日誌記錄及異常處理
	defer func() {
		costtime := (time.Now().UnixNano() - startTime.UnixNano()) / 1000000
		responseInfo.CostTime = strconv.FormatInt(costtime, 10)
		if err := recover(); err != nil {
			executeFlag = "N"
			errLog := fmt.Sprintf("[wheel.AllPurpose] defer error:%v", err)
			log.LOGGER("SUBX").Error(errLog)
			responseInfo.Rc = "999"
			responseInfo.Rm = "系統異常，" + errLog
		}
		jsonStr, _ := json.Marshal(responseInfo)
		if executeFlag == "N" || utils.Iswritetsdb() == "Y" {
			go utils.InfluxLogDataNew("wheel.AllPurpose", "", strconv.FormatInt(costtime, 10), c.Request.RequestURI,
				requestInfo.Function, requestInfo.RequestID, executeFlag, string(reqBody), string(jsonStr), c.RemoteIP(), "", "", startTimeStr, "", false, false)
		}
		c.JSON(http.StatusOK, responseInfo)
	}()

	if reqErr != nil || reqBody == nil {
		executeFlag = "N"
		responseInfo.Rc = "5910"
		responseInfo.Rm = "傳參解析異常"
		return
	}
	if len(reqBody) == 0 {
		executeFlag = "N"
		responseInfo.Rc = "5911"
		responseInfo.Rm = "傳參不能為空"
		return
	}
	// 非空欄位驗證

	notNullFields := []string{"function", "params", "uuid"}
	for _, field := range notNullFields {
		fieldvalue, fieldErr := jsonparser.GetUnsafeString(reqBody, field)
		if fieldErr != nil {
			responseInfo.Rc = "5913"
			responseInfo.Rm = field + "參數轉換異常"
			executeFlag = "N"
			return
		} else if len(fieldvalue) == 0 {
			responseInfo.Rc = "5914"
			responseInfo.Rm = field + "參數不能為空"
			executeFlag = "N"
			return
		}
	}
	//轉換JSON
	err := json.Unmarshal(reqBody, &requestInfo)
	if err != nil {
		executeFlag = "N"
		responseInfo.Rc = "5912"
		responseInfo.Rm = "JSON轉換異常"
		return
	}
	if len(requestInfo.RequestID) > 0 {
		responseInfo.RequestUuid = requestInfo.RequestID
	} else {
		responseInfo.RequestUuid = uuid.NewV4().String()
	}
	//校验uuid是否存在
	sql := `
		select count(1) from client_uuid where client_uuid = $1
	`
	result, err := utils.GetAllData(sql, requestInfo.Uuid)
	if err != nil {
		executeFlag = "N"
		errInfo := fmt.Sprintf("[wheel.AllPurpose] Func SQL execute error:%v", err)
		responseInfo.Rc = "400"
		responseInfo.Rm = "www.subtitlex.xyz/Jable-Helper"
		log.LOGGER("SUBX").Error(errInfo)
		return
	}
	if result[0]["count"].(int64) < 1 {
		responseInfo.Rc = "401"
		responseInfo.Rm = "www.subtitlex.xyz/Jable-Helper"
		return
	}

	//查询存储过程匿名表
	sql = `
		select function_name from functionmap where uuid = $1
	`
	result, err = utils.GetAllData(sql, requestInfo.Function)
	if err != nil {
		executeFlag = "N"
		errInfo := fmt.Sprintf("[wheel.AllPurpose] Func SQL execute error:%v", err)
		responseInfo.Rc = "5001"
		responseInfo.Rm = errInfo
		log.LOGGER("SUBX").Error(errInfo)
		return
	}

	if len(result) < 1 {
		responseInfo.Rc = "402"
		responseInfo.Rm = "www.subtitlex.xyz/Jable-Helper"
		return
	}

	function_name := result[0]["function_name"].(string)

	//調用存儲過程
	sqlStr := "select * from " + function_name + "("
	inParams := make([]interface{}, 0)
	paramsCount := 1
	for _, param := range requestInfo.Params {
		sqlStr += "$" + strconv.Itoa(paramsCount) + ","
		inParams = append(inParams, param)
		paramsCount++
	}
	sqlStr = string([]rune(sqlStr)[:len(sqlStr)-1]) + ")"

	rows, err := utils.GetAllData(sqlStr, inParams...)
	if err != nil {
		executeFlag = "N"
		errInfo := fmt.Sprintf("[wheel.AllPurpose] Func SQL execute error:%v", err)
		responseInfo.Rc = "5001"
		responseInfo.Rm = errInfo
		log.LOGGER("SUBX").Error(errInfo)
		return
	}
	responseInfo.Rc = "000"
	responseInfo.Rm = "OK"

	val, ok := rows[0]["o_resultcode"]
	if ok && val != nil {
		responseInfo.Rc = val.(string)
	}
	val, ok = rows[0]["o_resultmsg"]
	if ok && val != nil {
		responseInfo.Rm = val.(string)
	}
	val, ok = rows[0]["o_data"]
	if ok && val != nil {
		responseInfo.Data = val.(string)
	}
}
