package user

import (
	"goapi/src/dao"
	"goapi/src/model"
	"time"
)

func CheckIfInLimit(user model.User, subtitleUuid string) bool { // inLimit
	//TODO 考虑增加逻辑，去vercel接口校验用户信息
	if user.Email != "" { //已登录
		if user.HasSub { //有订阅
			expireDate := user.ExpireDate
			//1714460795554  毫秒
			//1714538617 //微秒
			currentTime := time.Now().UnixNano()  //纳秒
			if expireDate*1000000 > currentTime { //订阅有效
				return true
			}
		}
	}
	//根据邮箱或者客户uuid，查看用户今天已经获取过的subtitle数量
	//如果subtitle数量小于5，则可以获取subtitle
	subtitleUuids := dao.GetTodayVisitedSubtitlesByUser(user.Email, user.Uuid)
	if len(subtitleUuids) < 5 { //不足5个，允许继续请求
		return true
	}
	for _, uuid := range subtitleUuids { //达到5个，如果请求之前看过的，依然允许
		if subtitleUuid == uuid {
			return true
		}
	}
	return false
}
