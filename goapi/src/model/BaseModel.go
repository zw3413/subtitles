package model

type ResponseInfo struct {
	Rc          string `json:"rc"`
	Rm          string `json:"rm"`
	RequestUuid string `json:"request_id"`
	CostTime    string `json:"costtime"`
	//Data        []map[string]interface{} `json:"data"`
	Data string `json:"data"`
}
