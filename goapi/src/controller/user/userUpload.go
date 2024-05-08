package user

import (
	"encoding/json"
	"fmt"
	"goapi/src/dao"
	"goapi/src/model"
	"goapi/src/utils"
	"net/http"
	"path"
	"runtime"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	log "github.com/jeanphorn/log4go"
)

func UserUpload(c *gin.Context) {
	executeFlag := "Y"
	errMsg := ""
	var responseInfo model.ResponseInfo
	startTime := time.Now()
	startTimeStr := startTime.Format("20060102150405")
	function_name := "UserUpload"
	client_uuid := ""

	//日誌記錄及異常處理
	defer func() {
		costtime := (time.Now().UnixNano() - startTime.UnixNano()) / 1000000
		responseInfo.CostTime = strconv.FormatInt(costtime, 10)
		if err := recover(); err != nil {
			executeFlag = "N"
			errLog := fmt.Sprintf("[wheel.AllPurpose_external] defer error:%v", err)
			log.LOGGER("SUBX").Error(errLog)
			responseInfo.Rc = "996"
			responseInfo.Rm = "系統異常，" + errLog
		}
		jsonStr, _ := json.Marshal(responseInfo)
		if executeFlag == "N" || utils.Iswritetsdb() == "Y" {
			go utils.InfluxLogDataNew("wheel.AllPurpose_external", "", strconv.FormatInt(costtime, 10), c.Request.RequestURI,
				function_name, client_uuid, executeFlag, "", string(jsonStr), c.ClientIP(), "", errMsg, startTimeStr, "", false, false)
		}
		c.JSON(http.StatusOK, responseInfo)
	}()

	file, _ := c.FormFile("file")
	filename := c.PostForm("filename")
	//video_no := c.Query("video_no")
	language := "unknown"
	format := path.Ext(filename)
	seed_uuid := c.PostForm("uuid")
	source := "user_upload"

	filepath := "user_upload/" + startTime.Format("20060102") + "_" + filename
	dst := "../file/subtitle/" + filepath
	//将\替换成/
	ostype := runtime.GOOS
	if ostype == "windows" {
		dst = strings.Replace(dst, "/", "\\", -1)
	}
	//计算md5
	md5, err := utils.FileHash(dst)
	if err != nil {
		executeFlag = "N"
		errMsg = err.Error()
		responseInfo.Rc = "998"
		responseInfo.Rm = "上傳失敗"
		return
	}
	//存入数据库
	saved, err := dao.SaveUserUploadSubtitle(language, filepath, format, seed_uuid, source, md5)
	if err != nil {
		executeFlag = "N"
		errMsg = err.Error()
		responseInfo.Rc = "999"
		responseInfo.Rm = "上傳失敗"
		return
	}
	if saved != "saved" {
		executeFlag = "N"
		errMsg = err.Error()
		responseInfo.Rc = "000"
		responseInfo.Rm = "OK_002"
		return
	}
	err = c.SaveUploadedFile(file, dst)
	if err != nil {
		executeFlag = "N"
		errMsg = err.Error()
		responseInfo.Rc = "997"
		responseInfo.Rm = "上傳失敗"
		return
	}
}
