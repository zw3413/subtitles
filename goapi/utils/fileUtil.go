package utils

import (
	"errors"
	"io/ioutil"
)

// https://www.cnblogs.com/jrzh/p/15439361.html
// func ReadFile(filePath string) string {
// 	f, err := os.Open(filePath)
// 	if err != nil {
// 		fmt.Println("err:", err)
// 		return err.Error()
// 	}
// 	defer f.Close()

// 	content, err := readAllContent(f)
// 	if err != nil {
// 		fmt.Println("err:", err)
// 		return err.Error()
// 	}
// 	return content
// }

// func readAllContent(r io.Reader) (string, error) {
// 	var b = make([]byte, 4096)
// 	_, err := r.Read(b)
// 	if err != nil {
// 		return "", err
// 	}

// 	//l := strings.Split(string(b), "\r\n")
// 	return string(b), nil
// }

func ReadFile(filePath string) (string, error) {
	content, error := ioutil.ReadFile(filePath)
	if error != nil {
		return "", errors.New("err38291, not found")
	}
	str := string(content)
	return str, nil
}
