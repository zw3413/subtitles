package controller

import (
	"encoding/json"
	"fmt"
	jsonResponse "goapi/src/library/response"
	"goapi/src/utils"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	log "github.com/jeanphorn/log4go"
)

func UploadFiles(c *gin.Context) {
	function_name := "UploadFiles"
	client_uuid := ""
	executeFlag := "Y"
	startTime := time.Now()
	startTimeStr := startTime.Format("20060102150405")
	var resp jsonResponse.JsonResponse
	var filename string

	//日誌記錄及異常處理
	defer func() {
		costtime := (time.Now().UnixNano() - startTime.UnixNano()) / 1000000
		resp.Cost = strconv.FormatInt(costtime, 10)
		if err := recover(); err != nil {
			executeFlag = "N"
			errLog := fmt.Sprintf("[wheel.AllPurpose_external] defer error:%v", err)
			log.LOGGER("SUBX").Error(errLog)
			resp = jsonResponse.JsonFailMsg(errLog)
		}
		jsonStr, _ := json.Marshal(resp)
		if executeFlag == "N" || utils.Iswritetsdb() == "Y" {
			go utils.InfluxLogDataNew("ts_uploadfiles", filename, strconv.FormatInt(costtime, 10), c.Request.RequestURI,
				function_name, client_uuid, executeFlag, "", string(jsonStr), c.ClientIP(), "", "", startTimeStr, "", false, false)
		}
		c.JSON(http.StatusOK, resp)
	}()
	// 单文件
	file, _ := c.FormFile("file")
	// 上传文件到指定的路径
	filename = c.Query("filename")
	// dst := "../file/subtitle/" + filename
	// ostype := runtime.GOOS
	// if ostype == "windows" {
	// 	dst = strings.Replace(dst, "/", "\\", -1)
	// }
	// //将\替换成/
	// c.SaveUploadedFile(file, dst)
	dst, _, err := utils.SaveUploadedFile(c, file, filename)
	if err != nil {
		executeFlag = "N"
		log.LOGGER("SUBX").Error(err)
		resp = jsonResponse.JsonFailErr(err)
		return
	}
	resp = jsonResponse.JsonSuccessData(dst)
}

func PushSrtFile(c *gin.Context) {
	function_name := "PushSrtFile"
	client_uuid := ""
	executeFlag := "Y"
	startTime := time.Now()
	startTimeStr := startTime.Format("20060102150405")
	var resp jsonResponse.JsonResponse
	var filename string

	//日誌記錄及異常處理
	defer func() {
		costtime := (time.Now().UnixNano() - startTime.UnixNano()) / 1000000
		resp.Cost = strconv.FormatInt(costtime, 10)
		if err := recover(); err != nil {
			executeFlag = "N"
			errLog := fmt.Sprintf("[wheel.AllPurpose_external] defer error:%v", err)
			log.LOGGER("SUBX").Error(errLog)
			resp = jsonResponse.JsonFailMsg(errLog)
		}
		jsonStr, _ := json.Marshal(resp)
		if executeFlag == "N" || utils.Iswritetsdb() == "Y" {
			go utils.InfluxLogDataNew("ts_uploadfiles", filename, strconv.FormatInt(costtime, 10), c.Request.RequestURI,
				function_name, client_uuid, executeFlag, "", string(jsonStr), c.ClientIP(), "", "", startTimeStr, "", false, false)
		}
		c.JSON(http.StatusOK, resp)
	}()
	// 单文件
	file, _ := c.FormFile("file")
	// 上传文件到指定的路径
	filename = c.Query("filename")

	// dst := "../file/subtitle/" + filename

	// ostype := runtime.GOOS
	// if ostype == "windows" {
	// 	dst = strings.Replace(dst, "/", "\\", -1)
	// }
	// //将\替换成/
	// c.SaveUploadedFile(file, dst)
	dst, _, err := utils.SaveUploadedFile(c, file, filename)
	if err != nil {
		log.LOGGER("SUBX").Error(err)
		resp = jsonResponse.JsonFailErr(err)
		return
	}
	resp = jsonResponse.JsonSuccessData(dst)
}
