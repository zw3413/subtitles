package request

import (
	"encoding/json"
	"errors"
	"io/ioutil"

	"github.com/gin-gonic/gin"
)

func ReadBody(c *gin.Context) ([]byte, error) {
	var (
		requestBody []byte
		err         error
	)
	if requestBody, err = ioutil.ReadAll(c.Request.Body); err != nil {
		return nil, err
	} else {
		return requestBody, nil
	}
}
func ReadBodySimpleArray(c *gin.Context) ([]interface{}, error) {

	body, err := ReadBody(c)
	if err != nil {
		return nil, err
	}

	bodyArray := make([]interface{}, 0)
	if err = json.Unmarshal(body, &bodyArray); err != nil {
		return nil, err
	}
	return bodyArray, nil
}

func ReadQuery(c *gin.Context, name string, required bool) (interface{}, error) {
	value := c.Query(name)
	if required && len(value) == 0 {
		return nil, errors.New("query param required: " + name)
	}
	return value, nil
}
func ReadQueryStr(c *gin.Context, name string, required bool) (string, error) {
	if value, err := ReadQuery(c, name, required); err != nil {
		return "", err
	} else {
		return value.(string), nil
	}

}
func ReadQueryInt(c *gin.Context, name string, required bool) (int, error) {
	if value, err := ReadQuery(c, name, required); err != nil {
		return 0, err
	} else {
		return value.(int), nil
	}
}
