package controller

import (
	"fmt"
	"goapi/dao"
	"goapi/utils"
	"log"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

var filePath_prefix = "../file/subtitle/"

func getString(value interface{}) string {
	if value == nil {
		return ""
	} else {
		return value.(string)
	}
	//return value == nil ? "": value.(string)
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
	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered in f", r)
			c.JSON(500, "error")
			return
		}
		if err != nil {
			log.Println(err)
			c.JSON(500, "error")
		} else {
			c.JSON(200, "success")
		}
	}()
	json := make(map[string]interface{})
	c.BindJSON(&json)

	seed_id := getString(json["seed_id"])
	path := getString(json["path"])
	language := getString(json["language"])
	format := getString(json["format"])

	_, err = dao.InsertSubtitle(seed_id, path, language, format)

}

// 新增一个新的seed
func SaveSeed(c *gin.Context) {
	var err error
	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered in f", r)
			c.JSON(500, "error")
			return
		}
		if err != nil {
			log.Println(err)
			c.JSON(500, "error")
		} else {
			c.JSON(200, "success")
		}
	}()
	json := make(map[string]interface{})
	c.BindJSON(&json)
	id := getString(json["id"])
	video_no := getString(json["video_no"])
	video_name := getString(json["video_name"])
	video_page_url := getString(json["video_page_url"])
	video_m3u8_url := getString(json["video_m3u8_url"])
	mp3_path := getString(json["mp3_path"])
	srt_path := getString(json["srt_path"])
	video_language := getString(json["video_language"])
	video_desc := getString(json["video_desc"])
	process_status := getString(json["process_status"])
	err_msg := getString(json["err_msg"])

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
			println("Recovered in f", r)
			c.JSON(500, "error")
			return
		}
		if err != nil {
			log.Println(err)
			c.JSON(500, "error")
			return
		}
		c.JSON(200, data)
	}()

	hint := c.Query("hint")
	data, err = dao.SelectSeed(hint)
}

// func GetSeedByUrl(c *gin.Context) {
// 	var err error
// 	var data []map[string]interface{}
// 	defer func() {
// 		if r := recover(); r != nil {
// 			println("Recovered in f", r)
// 			c.JSON(500, "error")
// 			return
// 		}
// 		if err != nil {
// 			log.Println(err)
// 			c.JSON(500, "error")
// 			return
// 		}
// 		c.JSON(200, data)
// 	}()

// 	json := make(map[string]interface{})
// 	c.BindJSON(&json)
// 	//id := getString(json["id"])
// 	pageUrl := getString(json["pageurl"])

// 	if len(pageUrl) == 0 {
// 		panic("pageUrl is null")
// 	}
// 	//r, _ := dao.GetSeedByCondition(pageUrl, m3u8Url, video_name, video_no)
// }

func GetSeedNeedProcess(c *gin.Context) {
	var err error
	var data []map[string]interface{}
	defer func() {
		if r := recover(); r != nil {
			println("Recovered in f", r)
			c.JSON(500, "error")
			return
		}
		if err != nil {
			log.Println(err)
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
			log.Println("Recovered in f", r)
			c.JSON(500, "error")
		}
		if err != nil {
			log.Println("错误")
			log.Println(err)
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
			log.Println("Recovered in f", r)
			c.JSON(500, "error")
		}
		if err != nil {
			log.Println("错误")
			log.Println(err)
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

type Seed struct {
	id       string `json:"id"`
	language string `json:"language"`
}

func GetSubtitle1(c *gin.Context) {
	var err error
	var result string
	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered in f", r)
			c.JSON(500, "error")
		}
		if err != nil {
			log.Println("错误")
			log.Println(err)
			c.JSON(500, "error")
		} else {
			c.String(200, result)
		}
	}()
	//id := getString(json["id"])
	id := c.Query("id")
	language := c.Query("language")

	if len(id) == 0 || id == "null" {
		log.Println("错误")
		log.Println(err)
		c.JSON(500, "error，id is null")
		return
	}
	if len(language) == 0 || language == "null" {
		log.Println("错误")
		log.Println(err)
		c.JSON(500, "error，language is null")
		return
	}

	path, err := os.Getwd()
	if err != nil {
		log.Println(err)
	}
	log.Println(path)

	r, _ := dao.GetSubtitle_BySeedIdAndLanguage(id, language) //返回srt路径
	fileName := r[0]["path"].(string)
	filePath := filepath.Join(path, filePath_prefix, fileName)

	result = utils.ReadFile(filePath)

}

func GetSubtitle(c *gin.Context) {
	var err error
	var result string
	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered in f", r)
			c.JSON(500, "error")
		}
		if err != nil {
			log.Println("错误")
			log.Println(err)
			c.JSON(500, "error")
		} else {
			c.JSON(200, result)
		}
	}()
	json := make(map[string]interface{})
	c.BindJSON(&json)
	//id := getString(json["id"])
	id := getString(json["id"])
	language := getString(json["language"])

	if len(id) == 0 {
		panic("id is null")
	}
	if len(language) == 0 {
		language = "en"
	}

	path, err := os.Getwd()
	if err != nil {
		log.Println(err)
	}
	log.Println(path)

	r, _ := dao.GetSubtitle_BySeedIdAndLanguage(id, language) //返回srt路径
	fileName := r[0]["path"].(string)
	//filePath := path + "/" + filePath_prefix + r
	filePath := filepath.Join(path, filePath_prefix, fileName)

	result = utils.ReadFile(filePath)

}

func GetSubtitleInfo(c *gin.Context) {
	var err error
	var result []map[string]interface{}
	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered in f", r)
			c.JSON(500, "error")
		}
		if err != nil {
			log.Println("错误")
			log.Println(err)
			c.JSON(500, "error")
		} else {
			c.JSON(200, result)
		}
	}()
	//id := getString(json["id"])
	id := c.Query("id")
	language := c.Query("lang")

	if len(id) == 0 {
		panic("id is null")
	}
	// if len(language) == 0 {
	// 	panic("lang is null")
	// }

	if err != nil {
		log.Println(err)
	}
	r, _ := dao.GetSubtitle_BySeedIdAndLanguage(id, language) //返回srt路径
	result = r
}

func CmdPythonProduceSubtitle(m3u8Url string) (string, error) {
	args := []string{"./pytool/main.py", "ProduceSubtitle", m3u8Url}
	out, err := exec.Command("python", args...).Output()
	if err != nil {
		log.Println(err)
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
			println("Recovered in f", r)
			c.JSON(500, "error")
			return
		}
		if err != nil {
			log.Println(err)
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
			println("Recovered in f", r)
			c.JSON(500, "error")
			return
		}
		if err != nil {
			log.Println(err)
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
			println("Recovered in f", r)
			c.String(500, "error")
			return
		}
		if err != nil {
			log.Println(err)
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
			log.Println(err)
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
			log.Println(err)
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
			log.Println(err)
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
