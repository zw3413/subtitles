package main

import (
	"fmt"
	"goapi/src/configs"
	"goapi/src/controller"
	"goapi/src/controller/user"
	"goapi/src/controller/wheel"
	"goapi/src/dao"
	"goapi/src/library/response"
	"net/http"
	"os/exec"
	"runtime"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	log "github.com/jeanphorn/log4go"
)

var iniConfig *configs.Config

func init() {
	iniConfig = new(configs.Config)
	path := configs.GetProjectPath()
	log.LoadConfiguration(path + "/logconf.json")
	iniConfig.InitConfig()

	log.LOGGER("SUBX").Info("Server Start")
}

func main() {

	defer func() {
		if err := recover(); err != nil {
			errLog := fmt.Sprintf("[SaveSubtitle] defer error:%v", err)
			log.LOGGER("SUBX").Error(errLog)
		}
		if dao.Db != nil {
			dao.Db.Close()
		}
	}()

	//startPyTool() //启动python工具，定时从数据库中获取需要下载的字幕

	gin.SetMode(gin.DebugMode)
	r := gin.Default()

	//load the index page
	r.LoadHTMLFiles("./subtitle/index.html")
	//mapping the static resources
	//r.LoadHTMLFiles("./movie/player.html")

	r.Static("/static", "./subtitle/static/")
	//register the index page
	r.GET("/page/subtitle", func(c *gin.Context) {
		c.HTML(http.StatusOK, "index.html", nil)
	})
	// r.GET("/page/player", func(c *gin.Context) {
	// 	c.HTML(http.StatusOK, "player.html", nil)
	// })
	r.Use(CrosHandler())
	r.POST("/save_seed", controller.SaveSeed)
	r.POST("/get_seed", controller.GetSeed)

	r.POST("/save_subtitle", controller.SaveSubtitle)
	r.POST("/want_subtitle", controller.WantSubtitle)
	r.POST("/check_subtitle", controller.CheckSubtitle)
	r.GET("/get_subtitle", controller.GetSubtitle1)
	r.POST("/subtitle", controller.GetSubtitleWithUUID)
	//r.POST("/get_subtitle", controller.GetSubtitle)
	r.POST("get_subtitle_info", controller.GetSubtitleInfo)
	r.POST("/seed_need_process", controller.GetSeedNeedProcess)
	r.POST("/get_wants_not_process", controller.GetWantsNotProcess)
	r.POST("/get_want_seed", controller.WantSeed)
	r.POST("/check_if_wanted", controller.CheckIfWanted)
	r.POST("/update_want_fullfilled", controller.WantFullfilled)
	//r.POST("/check_save_get_seed", controller.CheckSaveGetSeed)
	r.POST("/common/allPurpose", wheel.AllPurpose) //數據庫函數調用通用接口
	r.POST("/api1", wheel.AllPurpose_external)     //數據庫函數調用通用接口
	r.POST("/api2", controller.Client_UUID)        //用户开启浏览器时，根据ip地址获取uuid
	r.POST("/api3", user.UserUpload)
	r.POST("/pushSrtFile", func(c *gin.Context) {
		// 单文件
		file, _ := c.FormFile("file")
		// 上传文件到指定的路径
		filename := c.Query("filename")

		dst := "../file/subtitle/" + filename

		ostype := runtime.GOOS
		if ostype == "windows" {
			dst = strings.Replace(dst, "/", "\\", -1)
		}
		//将\替换成/
		c.SaveUploadedFile(file, dst)
		c.JSON(http.StatusOK, response.JsonSuccessData(dst))
	})
	r.POST("/upload-files", func(c *gin.Context) {
		// 单文件
		file, _ := c.FormFile("file")
		// 上传文件到指定的路径

		filename := c.Query("filename")

		dst := "../file/subtitle/" + filename

		ostype := runtime.GOOS
		if ostype == "windows" {
			dst = strings.Replace(dst, "/", "\\", -1)
		}
		//将\替换成/
		c.SaveUploadedFile(file, dst)
		c.JSON(http.StatusOK, response.JsonSuccessData(dst))
	})
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "pong",
		})
	})
	r.Run(":12801")
}

func startPyTool() {
	go func() {
		for {
			out, err := exec.Command("python3", "../pytool/main.py", "download").Output()
			if err != nil {
				log.LOGGER("SUBX").Error("PyTool error and exit.")
				log.LOGGER("SUBX").Error(err)
			}
			log.LOGGER("SUBX").Info(string(out))
			//go routione sleep for 1 second
			time.Sleep(5 * time.Second)
		}
	}()

	go func() {
		for {
			out, err := exec.Command("python3", "../pytool/main.py", "transcribe").Output()
			if err != nil {
				log.LOGGER("SUBX").Error("PyTool error and exit.")
				log.LOGGER("SUBX").Error(err)
			}
			log.LOGGER("SUBX").Info(string(out))
			//go routione sleep for 1 second
			time.Sleep(5 * time.Second)
		}
	}()

}

// 跨域访问：cross  origin resource share
func CrosHandler() gin.HandlerFunc {
	return func(context *gin.Context) {
		method := context.Request.Method
		context.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		context.Header("Access-Control-Allow-Origin", "*") // 设置允许访问所有域
		context.Header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE,UPDATE")
		context.Header("Access-Control-Allow-Headers", "Authorization, Content-Length, X-CSRF-Token, Token,session,X_Requested_With,Accept, Origin, Host, Connection, Accept-Encoding, Accept-Language,DNT, X-CustomHeader, Keep-Alive, User-Agent, X-Requested-With, If-Modified-Since, Cache-Control, Content-Type, Pragma,token,openid,opentoken")
		context.Header("Access-Control-Expose-Headers", "Content-Length, Access-Control-Allow-Origin, Access-Control-Allow-Headers,Cache-Control,Content-Language,Content-Type,Expires,Last-Modified,Pragma,FooBar")
		context.Header("Access-Control-Max-Age", "172800")
		context.Header("Access-Control-Allow-Credentials", "false")
		context.Set("content-type", "application/json")

		if method == "OPTIONS" {
			context.JSON(http.StatusOK, "{'state':1,'msg':'success','data':{}}")
		} else {
			//处理请求
			context.Next()
		}

	}
}
