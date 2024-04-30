package configs

import (
	"bufio"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
)

const middle = "====="

type Config struct {
	Mymap  map[string]string
	strcet string
}

var (
	ostype    = runtime.GOOS
	iniConfig = new(Config)
)

func init() {
	iniConfig.InitConfig()
}

func GetProjectPath() string {
	var projectPath string
	projectPath, _ = filepath.Abs(filepath.Dir(os.Args[0]))
	//fmt.Printf(projectPath)
	return projectPath
}

func existPath(path string) error {
	_, err := os.Stat(path)
	if err != nil {
		err = os.MkdirAll(path, os.ModePerm)
		if err != nil {
			return err
		}
	}
	return nil
}

func substr(s string, pos, length int) string {
	runes := []rune(s)
	l := pos + length
	if l > len(runes) {
		l = len(runes)
	}
	return string(runes[pos:l])
}

func GetParentDirectory(dir string) string {
	return substr(dir, 0, strings.LastIndex(dir, "\\"))
}

func GetCurrentDirectory() string {
	dir, err := filepath.Abs(filepath.Dir(os.Args[0]))
	if err != nil {
		log.Fatal(err)
	}
	// return strings.Replace(dir, "\\", "/", -1)
	return dir
}

func (c *Config) InitConfig() {
	configPath := GetProjectPath()
	var path string
	if ostype == "windows" {
		path = configPath + "\\config.ini"
	} else if ostype == "linux" {
		path = configPath + "/config.ini"
	}

	c.Mymap = make(map[string]string)

	f, err := os.Open(path)
	if err != nil {
		fmt.Println(err)
	}
	defer f.Close()

	r := bufio.NewReader(f)
	for {
		b, _, err := r.ReadLine()
		if err != nil {
			if err == io.EOF {
				break
			}
			fmt.Println(err)
		}

		s := strings.TrimSpace(string(b))
		//fmt.Println(s)
		if strings.Index(s, "#") == 0 {
			continue
		}

		n1 := strings.Index(s, "[")
		n2 := strings.LastIndex(s, "]")
		if n1 > -1 && n2 > -1 && n2 > n1+1 {
			c.strcet = strings.TrimSpace(s[n1+1 : n2])
			continue
		}

		if len(c.strcet) == 0 {
			continue
		}
		index := strings.Index(s, "=")
		if index < 0 {
			continue
		}

		frist := strings.TrimSpace(s[:index])
		if len(frist) == 0 {
			continue
		}
		second := strings.TrimSpace(s[index+1:])

		pos := strings.Index(second, "\t#")
		if pos > -1 {
			second = second[0:pos]
		}

		pos = strings.Index(second, " #")
		if pos > -1 {
			second = second[0:pos]
		}

		pos = strings.Index(second, "\t//")
		if pos > -1 {
			second = second[0:pos]
		}

		pos = strings.Index(second, " //")
		if pos > -1 {
			second = second[0:pos]
		}

		if len(second) == 0 {
			continue
		}

		key := c.strcet + middle + frist
		c.Mymap[key] = strings.TrimSpace(second)
	}
}

func (c Config) Read(node, key string) string {
	key = node + middle + key
	value, found := c.Mymap[key]
	if !found {
		return ""
	}
	return value
}

func (c Config) ReadInt(node, key string) int {
	key = node + middle + key
	value, found := c.Mymap[key]
	if !found {
		return 0
	}
	i, err := strconv.Atoi(value)
	if err != nil {
		return 0
	}
	return i
}
