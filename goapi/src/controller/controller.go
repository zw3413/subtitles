package controller

import (
	"encoding/json"
	"fmt"
	"goapi/src/controller/user"
	"goapi/src/dao"
	"goapi/src/model"
	"goapi/src/utils"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	log "github.com/jeanphorn/log4go"
)

var filePath_prefix = "../file/subtitle/"

// hashcode: "xxx",
// request_id: "xxx",
// device_ip: "0.0.0.0",
// user: user,
type RequestObj struct {
	Hashcode  string     `json:"hashcode"`
	RequestId string     `json:"request_id"`
	DeviceIp  string     `json:"device_ip"`
	User      model.User `json:"user"`
}
type Seed struct {
	id       string `json:"id"`
	language string `json:"language"`
}

func getString(value interface{}) string {
	if value == nil {
		return ""
	} else {
		return value.(string)
	}
}
func getInt(value interface{}) int {
	if value == nil {
		return -1
	} else {
		return value.(int)
	}
}
func SaveSubtitle(c *gin.Context) {
	var err error
	var errLog string
	executeFlag := "Y"
	var responseInfo model.ResponseInfo
	requestObj := make(map[string]interface{})
	startTime := time.Now()
	startTimeStr := startTime.Format("20060102150405")
	requestBody, err := io.ReadAll(c.Request.Body)
	var seed_id string
	defer func() {
		costtime := (time.Now().UnixNano() - startTime.UnixNano()) / 1000000
		responseInfo.CostTime = strconv.FormatInt(costtime, 10)

		responseInfo.Rc = "000"
		responseInfo.Rm = "OK"

		if err != nil {
			executeFlag = "N"
			errLog = fmt.Sprintf("[SaveSubtitle] defer error:%v", err)
			log.LOGGER("SUBX").Error(errLog)
			responseInfo.Rc = "998"
			responseInfo.Rm = "系統異常，" + errLog
		}

		if err := recover(); err != nil {
			executeFlag = "N"
			errLog = fmt.Sprintf("[SaveSubtitle] defer error:%v", err)
			log.LOGGER("SUBX").Error(errLog)
			responseInfo.Rc = "999"
			responseInfo.Rm = "系統異常，" + errLog
		}
		jsonStr, _ := json.Marshal(responseInfo)
		if executeFlag == "N" || utils.Iswritetsdb() == "Y" {
			go utils.InfluxLogDataNew("SaveSubtitle", seed_id, strconv.FormatInt(costtime, 10), c.Request.RequestURI,
				"", "", executeFlag, string(requestBody), string(jsonStr), c.ClientIP(), "", errLog, startTimeStr, "", false, false)
		}
		c.JSON(http.StatusOK, responseInfo)
	}()
	err = json.Unmarshal(requestBody, &requestObj)
	seed_id = getString(requestObj["seed_id"])
	path := getString(requestObj["path"])
	language := getString(requestObj["language"])
	format := getString(requestObj["format"])
	source := getString(requestObj["source"])
	origin_id := getString(requestObj["origin_id"])

	_, err = dao.InsertSubtitle(seed_id, path, language, format, source, origin_id)
}

// 新增一个新的seed
func SaveSeed(c *gin.Context) {
	var err error
	var errLog string
	executeFlag := "Y"
	var responseInfo model.ResponseInfo
	requestObj := make(map[string]interface{})
	startTime := time.Now()
	startTimeStr := startTime.Format("20060102150405")
	requestBody, err := io.ReadAll(c.Request.Body)
	var (
		id       string
		video_no string
	)
	//日誌記錄及異常處理
	defer func() {
		costtime := (time.Now().UnixNano() - startTime.UnixNano()) / 1000000
		responseInfo.CostTime = strconv.FormatInt(costtime, 10)

		responseInfo.Rc = "000"
		responseInfo.Rm = "OK"

		if err != nil {
			executeFlag = "N"
			errLog = fmt.Sprintf("[SaveSeed] defer error:%v", err)
			log.LOGGER("SUBX").Error(errLog)
			responseInfo.Rc = "998"
			responseInfo.Rm = "系統異常，" + errLog
		}

		if err := recover(); err != nil {
			executeFlag = "N"
			errLog = fmt.Sprintf("[SaveSeed] defer error:%v", err)
			log.LOGGER("SUBX").Error(errLog)
			responseInfo.Rc = "999"
			responseInfo.Rm = "系統異常，" + errLog
		}
		jsonStr, _ := json.Marshal(responseInfo)
		if executeFlag == "N" || utils.Iswritetsdb() == "Y" {
			go utils.InfluxLogDataNew("SaveSeed", id, strconv.FormatInt(costtime, 10), c.Request.RequestURI,
				"", "", executeFlag, string(requestBody), string(jsonStr), c.ClientIP(), "", errLog, startTimeStr, "", false, false)
		}
		c.JSON(http.StatusOK, responseInfo)
	}()

	err = json.Unmarshal(requestBody, &requestObj)
	id = getString(requestObj["id"])
	video_no = getString(requestObj["video_no"])
	video_name := getString(requestObj["video_name"])
	video_page_url := getString(requestObj["video_page_url"])
	video_m3u8_url := getString(requestObj["video_m3u8_url"])
	mp3_path := getString(requestObj["mp3_path"])
	srt_path := getString(requestObj["srt_path"])
	video_language := getString(requestObj["video_language"])
	video_desc := getString(requestObj["video_desc"])
	process_status := getString(requestObj["process_status"])
	err_msg := getString(requestObj["err_msg"])

	if id != "" {
		_, err = dao.UpdateSeed(id, video_no, video_name, video_page_url, video_m3u8_url, mp3_path, srt_path, video_language, video_desc, process_status, err_msg)
	} else {
		_, err = dao.InsertSeed(video_no, video_name, video_page_url, video_m3u8_url, mp3_path, srt_path, video_language, video_desc)
	}

}
func GetSeed(c *gin.Context) {
	var err error
	var data []map[string]interface{}
	defer func() {
		if r := recover(); r != nil {
			log.LOGGER("SUBX").Error(r)
			c.JSON(500, "error")
			return
		}
		if err != nil {
			log.LOGGER("SUBX").Error(err)
			c.JSON(500, "error")
			return
		}
		c.JSON(200, data)
	}()

	hint := c.Query("hint")
	data, err = dao.SelectSeed(hint)
}
func GetSeedNeedProcess(c *gin.Context) {
	var err error
	var data []map[string]interface{}
	defer func() {
		if r := recover(); r != nil {
			log.LOGGER("SUBX").Error(r)
			c.JSON(500, "error")
			return
		}
		if err != nil {
			log.LOGGER("SUBX").Error(err)
			c.JSON(500, "error")
			return
		}
		c.JSON(200, data)
	}()
	t := c.Query("type")
	data, err = dao.SelectSeedNeedProcess(t)
}
func WantSubtitle(c *gin.Context) {
	var err error
	var result []map[string]interface{}
	var msg string
	defer func() {
		if r := recover(); r != nil {
			log.LOGGER("SUBX").Error(r)
			c.JSON(500, "error")
		}
		if err != nil {
			log.LOGGER("SUBX").Error(err)
			c.JSON(500, "error")
		} else if result != nil {
			c.JSON(200, result)
		} else {
			c.JSON(200, msg)
		}
	}()
	json := make(map[string]interface{})
	c.BindJSON(&json)
	//id := getString(json["id"])
	pageUrl := getString(json["pageurl"])
	m3u8Url := getString(json["m3u8url"])
	video_name := getString(json["video_name"])
	video_no := getString(json["video_no"])
	video_desc := getString(json["video_desc"])
	want_language := getString(json["want_language"])

	clientIP := c.GetHeader("X-Forwarded-For")
	// If X-Forwarded-For is not present, fall back to RemoteAddr
	if clientIP == "" {
		clientIP = c.Request.RemoteAddr
	}

	//by以上条件从数据库找是否已有数据
	r, _ := dao.GetSeedByCondition(pageUrl, m3u8Url, video_name, video_no)

	if len(r) > 0 {
		seed_id := r[0]["id"].(int64)
		//已经有数据
		dao.IncreaseWantTime(r[0]["id"].(int64))

		//从subtitle表中查找seed_id和lang是否已经生成过
		fullfilled, wantedTimes := dao.CheckIfFullfilled(fmt.Sprint(seed_id), want_language)
		if fullfilled { //已经生成
			msg = "generated"
			dao.InsertWant(fmt.Sprint(seed_id), clientIP, want_language, "Y")
		} else { //已经提交过，还未生成
			if wantedTimes > 0 {
				msg = "generating"
			} else {
				msg = "submitted"
			}
			dao.InsertWant(fmt.Sprint(seed_id), clientIP, want_language, "N")
		}

		if r[0]["process_status"] == "2e" {
			dao.UpdateSeedProcessstatus(r[0]["id"].(int64), "1")
		} else if r[0]["process_status"] == "1e" {
			dao.UpdateSeedProcessstatus(r[0]["id"].(int64), "0")
		}

	} else {
		//需要新生成
		//videoNo, videoName, videoPageUrl, videoM3u8Url, mp3Path, srtPath, videoLanguage, videoDesc
		r, _ = dao.InsertSeed(video_no, video_name, pageUrl, m3u8Url, "", "", "", video_desc)
		seed_id := r[0]["id"].(int64)
		msg = "submitted"
		dao.InsertWant(fmt.Sprint(seed_id), clientIP, want_language, "N")
	}
}
func CheckSubtitle(c *gin.Context) {
	var err error
	var result []map[string]interface{}
	var msg string
	defer func() {
		if r := recover(); r != nil {
			log.LOGGER("SUBX").Error(r)
			c.JSON(500, "error")
		}
		if err != nil {
			log.LOGGER("SUBX").Error(err)
			c.JSON(500, "error")
		} else if result != nil {
			c.JSON(200, result)
		} else {
			c.JSON(200, msg)
		}
	}()
	json := make(map[string]interface{})
	c.BindJSON(&json)
	//id := getString(json["id"])
	pageUrl := getString(json["pageurl"])
	//m3u8Url := getString(json["m3u8url"])
	//video_name := getString(json["video_name"])
	video_no := getString(json["video_no"])
	//video_desc := getString(json["video_desc"])
	//want_language := getString(json["want_language"])

	r, _ := dao.GetSeedByPageUrl(pageUrl, video_no)
	result = r
}
func GetSubtitle1(c *gin.Context) {
	var err error
	var result, fileName string
	defer func() {
		if r := recover(); r != nil {
			log.LOGGER("SUBX").Error(r)
			c.JSON(500, "error")
		}
		if err != nil {
			c.JSON(500, err)
		} else {
			c.String(200, result)
		}
	}()
	path, err := os.Getwd()
	if err != nil {
		log.LOGGER("SUBX").Error(err)
	}
	srt_path := c.Query("srt_path")
	if len(srt_path) > 0 {
		fileName = srt_path
	} else {
		//id := getString(json["id"])
		id := c.Query("id")
		language := c.Query("language")
		subtitleId := c.Query("titleSubaId")
		seedUuid := c.Query("uuid")

		//id+language
		//uuid+language
		//subtitleId
		//以上三种情形，必须满足一种

		if len(id) == 0 && len(subtitleId) == 0 && len(seedUuid) == 0 {
			c.JSON(400, "error，id is null")
			return
		}
		if len(language) == 0 {
			language = "eng"
		}
		r, _ := dao.GetSubtitle_BySeedIdAndLanguage(id, seedUuid, subtitleId, language) //返回srt路径
		fileName = r[0]["path"].(string)
	}
	filePath := filepath.Join(path, filePath_prefix, fileName)
	result, err = utils.ReadFile(filePath)
}
func GetSubtitleWithUUID(c *gin.Context) {
	executeFlag := "Y" //执行成功标记
	var respCode int = 200
	var err error
	var request RequestObj
	var response string
	var errMsg string
	var uuid string
	var inLimit bool
	var filePath string
	var fileName string
	var user_email string
	var subscribed bool
	var inlimit bool
	startTime := time.Now()
	startTimeStr := startTime.Format("20060102150405")

	//解析请求信息，及用户信息
	reqBody, reqErr := io.ReadAll(c.Request.Body)
	defer func() {
		//接口用时
		costtime := (time.Now().UnixNano() - startTime.UnixNano()) / 1000000

		//恢复错误
		if r := recover(); r != nil {
			executeFlag = "N"
			errMsg = fmt.Sprintf("Recovered in GetSubtitleWithUUID, err=%v, costtime=%v", r, costtime)
			log.LOGGER("SUBX").Error(errMsg)
			respCode = 500
			response = "error"
		}
		//tsdb日志记录
		if executeFlag == "N" || utils.Iswritetsdb() == "Y" {
			go utils.InfluxLogDataNew("subtitlex", uuid, strconv.FormatInt(costtime, 10), c.Request.RequestURI,
				"GetSubtitleWithUUID", request.RequestId, executeFlag, string(reqBody), errMsg, c.ClientIP(), "", response, startTimeStr, user_email, subscribed, inlimit)
		}
		c.String(respCode, response)
	}()
	if reqErr != nil || reqBody == nil {
		executeFlag = "N"
		errMsg = reqErr.Error()
		log.LOGGER("SUBX").Error(reqErr)
		respCode = 400
		response = "error"
		return
	}
	err = json.Unmarshal(reqBody, &request)
	if err != nil {
		executeFlag = "N"
		errMsg = "解析参数json失败" + err.Error()
		log.LOGGER("SUBX").Error(err)
		respCode = 400
		response = "error"
		return
	}
	//非登录用户，进行权限控制
	uuid = c.Query("id")

	if len(uuid) == 0 {
		executeFlag = "N"
		errMsg = "id missing"
		log.LOGGER("SUBX").Error(errMsg)
		respCode = 400
		response = "error"
		return
	}

	inLimit, err = user.CheckIfInLimit(request.User, uuid)
	if err != nil {
		executeFlag = "N"
		errMsg = err.Error()
		log.LOGGER("SUBX").Error(err)
		respCode = 500
		response = "error"
		return
	}
	path, err := os.Getwd()
	if err != nil {
		executeFlag = "N"
		errMsg = err.Error()
		log.LOGGER("SUBX").Error(err)
		respCode = 500
		response = "error"
		return
	}
	if inLimit {
		r, _ := dao.GetSubtitle_ByUuid(uuid) //返回srt路径
		fileName = r[0]["path"].(string)
		filePath = filepath.Join(path, filePath_prefix, fileName)
		response, err = utils.ReadFile(filePath)
		if err != nil {
			executeFlag = "N"
			errMsg = err.Error()
			log.LOGGER("SUBX").Error(err)
			respCode = 500
			response = "error"
			return
		}
		if len(response) == 0 {
			executeFlag = "N"
			errMsg = "subtitle is null"
			log.LOGGER("SUBX").Error(errMsg)
			respCode = 500
			response = "error"
			return
		}
		err = dao.SaveSubtitleLog(request.User.Email, request.User.Uuid, uuid, "subtitle")
		if err != nil {
			executeFlag = "N"
			errMsg = err.Error()
			log.LOGGER("SUBX").Error(err)
			respCode = 500
			response = "error"
			return
		}
	} else {
		fileName = "overlimit.srt"
		filePath = filepath.Join(path, filePath_prefix, fileName)
		response, err = utils.ReadFile(filePath)
		if err != nil {
			executeFlag = "N"
			errMsg = err.Error()
			log.LOGGER("SUBX").Error(err)
			respCode = 500
			response = "error"
			return
		}
		if len(response) == 0 {
			executeFlag = "N"
			errMsg = "failed to read overlimit.srt"
			log.LOGGER("SUBX").Error(errMsg)
			respCode = 500
			response = "error"
			return
		}
	}
}
func GetSubtitleInfo(c *gin.Context) {
	var err error
	var result []map[string]interface{}
	defer func() {
		if r := recover(); r != nil {
			log.LOGGER("SUBX").Error(r)
			c.JSON(500, "error")
		}
		if err != nil {
			log.LOGGER("SUBX").Error(err)
			c.JSON(500, "error")
		} else {
			c.JSON(200, result)
		}
	}()
	//id := getString(json["id"])
	id := c.Query("id")
	language := c.Query("lang")
	subtitleId := c.Query("titleSubaId")
	seedUuid := c.Query("uuid")

	//id+language
	//uuid+language
	//subtitleId
	//以上三种情形，必须满足一种

	if len(id) == 0 && len(subtitleId) == 0 && len(seedUuid) == 0 {
		c.JSON(400, "error，id is null")
		return
	}
	if len(language) == 0 {
		language = "eng"
	}
	r, _ := dao.GetSubtitle_BySeedIdAndLanguage(id, seedUuid, subtitleId, language) //返回srt路径
	result = r
}
func CmdPythonProduceSubtitle(m3u8Url string) (string, error) {
	args := []string{"./pytool/main.py", "ProduceSubtitle", m3u8Url}
	out, err := exec.Command("python", args...).Output()
	if err != nil {
		log.LOGGER("SUBX").Error(err)
		return "", err
	}
	result := string(out)
	// if strings.Index(result, "success") != 0 {
	// 	err = errors.New(fmt.Sprintf("main.py error：%s", result))
	// }
	return result, nil
}
func GetWantsNotProcess(c *gin.Context) {
	var err error
	var data []map[string]interface{}
	defer func() {
		if r := recover(); r != nil {
			log.LOGGER("SUBX").Error(r)
			c.JSON(500, "error")
			return
		}
		if err != nil {
			log.LOGGER("SUBX").Error(err)
			c.JSON(500, "error")
			return
		}
		c.JSON(200, data)
	}()

	seed_id := c.Query("seed_id")
	data, err = dao.GetWantsNotProcess(seed_id)
}

func WantSeed(c *gin.Context) {
	var err error
	var data []map[string]interface{}
	defer func() {
		if r := recover(); r != nil {
			log.LOGGER("SUBX").Error(r)
			c.JSON(500, "error")
			return
		}
		if err != nil {
			log.LOGGER("SUBX").Error(err)
			c.JSON(500, "error")
			return
		}
		c.JSON(200, data)
	}()
	data, err = dao.WantSeed()
}
func CheckIfWanted(c *gin.Context) {
	var err error
	var data string
	defer func() {
		if r := recover(); r != nil {
			log.LOGGER("SUBX").Error(r)
			c.String(500, "error")
			return
		}
		if err != nil {
			log.LOGGER("SUBX").Error(err)
			c.String(500, "error")
			return
		}
		c.String(200, data)
	}()
	json := make(map[string]interface{})
	c.BindJSON(&json)
	seed_id := getString(json["seed_id"])
	want_lang := getString(json["want_lang"])
	data = dao.CheckIfWanted(seed_id, want_lang)

	if data == "yes" {
		clientIP := c.GetHeader("X-Forwarded-For")
		// If X-Forwarded-For is not present, fall back to RemoteAddr
		if clientIP == "" {
			clientIP = c.Request.RemoteAddr
		}
		//dao.InsertWant(fmt.Sprint(seed_id), clientIP, want_lang, "N")
	}
}
func WantFullfilled(c *gin.Context) {
	var err error
	var data []map[string]interface{}
	defer func() {
		if r := recover(); r != nil {
			println("Recovered in f", r)
			c.JSON(500, "error")
			return
		}
		if err != nil {
			log.LOGGER("SUBX").Error(err)
			c.JSON(500, "error")
			return
		}
		c.JSON(200, data)
	}()
	want_id := c.Query("want_id")
	fullfilled := c.Query("fullfilled")
	data, err = dao.WangFullfilled(want_id, fullfilled)
}
func CheckSaveGetSeed(c *gin.Context) {
	var err error
	var data response
	defer func() {
		if r := recover(); r != nil {
			println("Recovered in f", r)
			c.JSON(500, data)
			return
		}
		if err != nil {
			log.LOGGER("SUBX").Error(err)
			c.JSON(500, data)
			return
		}
		c.JSON(200, data)
	}()

	json := make(map[string]interface{})
	c.BindJSON(&json)
	//id := getString(json["id"])
	pageUrl := getString(json["pageurl"])
	m3u8Url := getString(json["m3u8url"])
	videoName := getString(json["video_name"])
	videoNo := getString(json["video_no"])
	videoDesc := getString(json["video_desc"])

	clientIP := c.GetHeader("X-Forwarded-For")
	// If X-Forwarded-For is not present, fall back to RemoteAddr
	if clientIP == "" {
		clientIP = c.Request.RemoteAddr
	}

	seed := seed{}
	// 1. 是否存在，不存在新增一条，并返回

	r, err := dao.GetSeedByCondition(pageUrl, m3u8Url, videoName, videoNo)
	if len(r) == 0 {
		result, err := dao.InsertSeed(videoNo, videoName, pageUrl, m3u8Url, "", "", "", videoDesc)
		if err != nil {
			log.LOGGER("SUBX").Error(err)
			data.rc = "500"
			data.rm = err.Error()
			return
		}
		seed.seed_id = result[0]["id"].(int64)
		seed.video_no = videoNo
		seed.video_name = videoName
		seed.video_page_url = pageUrl
		seed.video_m3u8_url = m3u8Url
		seed.video_desc = videoDesc
		data.data = seed
		return
	} else {
		//seed.seed_id
	}
	// 2. 存在的话，继续查找want表和subtitle表
	//data, err = dao.WantSeed()
}

func Client_UUID(c *gin.Context) {
	var err error
	var errLog string
	executeFlag := "Y"
	var responseInfo model.ResponseInfo
	startTime := time.Now()
	startTimeStr := startTime.Format("20060102150405")
	requestBody, err := io.ReadAll(c.Request.Body)
	var seed_id string
	var uuid string
	defer func() {
		costtime := (time.Now().UnixNano() - startTime.UnixNano()) / 1000000
		responseInfo.CostTime = strconv.FormatInt(costtime, 10)

		responseInfo.Rc = "000"
		responseInfo.Rm = "OK"

		if err != nil {
			executeFlag = "N"
			errLog = fmt.Sprintf("[Client_UUID] defer error:%v", err)
			log.LOGGER("SUBX").Error(errLog)
			responseInfo.Rc = "998"
			responseInfo.Rm = "系統異常，" + errLog
		}

		if err := recover(); err != nil {
			executeFlag = "N"
			errLog = fmt.Sprintf("[Client_UUID] defer error:%v", err)
			log.LOGGER("SUBX").Error(errLog)
			responseInfo.Rc = "999"
			responseInfo.Rm = "系統異常，" + errLog
		}
		jsonStr, _ := json.Marshal(responseInfo)
		if executeFlag == "N" || utils.Iswritetsdb() == "Y" {
			go utils.InfluxLogDataNew("api2", seed_id, strconv.FormatInt(costtime, 10), c.Request.RequestURI,
				"Client_UUID", uuid, executeFlag, string(requestBody), string(jsonStr), c.ClientIP(), "", errLog, startTimeStr, "", false, false)
		}
		c.JSON(http.StatusOK, responseInfo)
	}()
	clientIp := c.ClientIP()
	//去数据库client_uuid表中查其uuid
	uuid, err = dao.GetUuidByClientIp(clientIp)
	if err != nil {
		executeFlag = "N"
		errLog = fmt.Sprintf("[Client_UUID] defer error:%v", err)
		log.LOGGER("SUBX").Error(errLog)
		responseInfo.Rc = "999"
		responseInfo.Rm = "系統異常，" + errLog
		return
	}
	responseInfo.Rc = "000"
	responseInfo.Rm = "OK"
	responseInfo.Data = uuid
}

// func getClientIpAddr(req *http.Request) string {
// 	return req.RemoteAddr
// }
// func getClientIpAddrNginx(req *http.Request) string {
// 	clientIp := req.Header.Get("X-FORWARDED-FOR")
// 	if clientIp != "" {
// 		return clientIp
// 	}
// 	return req.RemoteAddr
// }

type response struct {
	rc   string      `json:"rc"`
	rm   string      `json:"rm"`
	cost int64       `json:"cost"`
	data interface{} `json:"data"`
}

type seed struct {
	seed_id        int64      `json:"seed_id"`
	video_no       string     `json:"video_no"`
	video_name     string     `json:"video_name"`
	video_m3u8_url string     `json:"video_m3u8_url"`
	video_page_url string     `json:"video_page_url"`
	video_language string     `json:"video_language"`
	video_desc     string     `json:"video_desc"`
	want           []want     `json:"want"`
	subtile        []subtitle `json:"subtle"`
}

type want struct {
	want_id       int    `json:"want_id"`
	seed_id       int    `json:"seed_id"`
	want_language string `json:"want_language"`
	want_status   string `json:"want_status"`
}

type subtitle struct {
	subtitle_id       int    `json:"subtitle_id"`
	seed_id           int    `json:"seed_id"`
	subtitle_language string `json:"subtitle_language"`
	subtitle_path     string `json:"subtitle_path"`
}
