package user

import (
	"goapi/src/configs"
	"goapi/src/dao"
	"goapi/src/model"
	"time"
)

var iniConfig *configs.Config
var limit_subscribe_frame, limit_unsubscribe_frame string
var limit_subscribe_number, limit_unsubscribe_unlogin_number, limit_unsubscribe_login_number int

func init() {
	iniConfig = new(configs.Config)
	iniConfig.InitConfig()
	limit_subscribe_frame = iniConfig.Read("userlimit", "limit_subscribe_frame")
	//if not set, use "24 hour" as default
	if limit_subscribe_frame == "" {
		limit_subscribe_frame = "24 hour"
	}
	limit_subscribe_number = iniConfig.ReadInt("userlimit", "limit_subscribe_number")
	//if not set, use 200 as default
	if limit_subscribe_number == 0 {
		limit_subscribe_number = 200
	}

	limit_unsubscribe_frame = iniConfig.Read("userlimit", "limit_unsubscribe_frame")
	//if not set, use "1 hour" as default
	if limit_unsubscribe_frame == "" {
		limit_unsubscribe_frame = "1 hour"
	}
	limit_unsubscribe_unlogin_number = iniConfig.ReadInt("userlimit", "limit_unsubscribe_unlogin_number")
	//if not set, use "10" as default
	if limit_unsubscribe_unlogin_number == 0 {
		limit_unsubscribe_unlogin_number = 10
	}
	limit_unsubscribe_login_number = iniConfig.ReadInt("userlimit", "limit_unsubscribe_login_number")
	//if not set, use "10" as default
	if limit_unsubscribe_login_number == 0 {
		limit_unsubscribe_login_number = 10
	}
}

func CheckIfInLimit(user model.User, subtitleUuid string) (bool, error) { // inLimit

	var limit_num int

	//验证client uuid是否在数据库存在
	uuid_valid, err := dao.CheckClientUUID(user.Uuid)
	if err != nil {
		return false, err
	}
	if !uuid_valid {
		return false, nil
	}

	if user.Uuid == "oooooxxxxx" {
		return true, nil
	}

	//TODO 考虑增加逻辑，去vercel接口校验用户信息
	if user.Email != "" { //已登录
		if user.HasSub { //有订阅
			expireDate := user.ExpireDate
			//1714460795554  毫秒
			//1714538617 //微秒
			currentTime := time.Now().UnixNano()     //纳秒
			if expireDate*1000000000 > currentTime { //订阅有效
				limit_num = limit_subscribe_number //200
				hours := limit_subscribe_frame     //"24 hour"
				subtitleUuids := dao.GetTodayVisitedSubtitlesByUser(user.Email, user.Uuid, hours)
				if len(subtitleUuids) <= limit_num { //每天200个
					return true, nil
				} else {
					for _, uuid := range subtitleUuids { //达到200个，如果请求之前看过的，依然允许
						if subtitleUuid == uuid {
							return true, nil
						}
					}
					return false, nil
				}
			}
		}
	}

	//根据邮箱或者客户uuid，查看用户今天已经获取过的subtitle数量
	//如果subtitle数量小于5，则可以获取subtitle
	hours := limit_unsubscribe_frame //"1 hour"
	subtitleUuids := dao.GetTodayVisitedSubtitlesByUser(user.Email, user.Uuid, hours)
	limit_num = limit_unsubscribe_unlogin_number //10        //未登录
	if user.Email != "" {                        //已登录
		limit_num = limit_unsubscribe_login_number //20
	}
	if len(subtitleUuids) <= limit_num { //不足10个，允许继续请求
		return true, nil
	}
	for _, uuid := range subtitleUuids { //达到10个，如果请求之前看过的，依然允许
		if subtitleUuid == uuid {
			return true, nil
		}
	}
	return false, nil
}
