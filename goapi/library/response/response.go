package response

// 数据返回通用JSON数据结构
type JsonResponse struct {
	State int         `json:"state"` // 错误码((1:成功, 0:失败, >1:错误码))
	Msg   string      `json:"msg"`   // 提示信息
	Data  interface{} `json:"data"`  // 返回数据(业务接口定义具体数据结构)
}

// 成功無數據
func JsonSuccess() JsonResponse {
	return Json(1, "success", nil)
}

// 成功返回结果
func JsonSuccessData(data interface{}) JsonResponse {
	return Json(1, "success", data)
}

// 失败返回message
func JsonFailMsg(msg string) JsonResponse {
	return Json(0, msg, nil)
}

// 失败返回error
func JsonFailErr(err error) JsonResponse {
	return Json(0, err.Error(), nil)
}

// 标准返回结果数据结构封装。
func Json(state int, msg string, data interface{}) JsonResponse {
	return JsonResponse{
		State: state,
		Msg:   msg,
		Data:  data,
	}
}
