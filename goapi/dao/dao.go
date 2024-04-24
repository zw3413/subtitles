package dao

import (
	"database/sql"
	"goapi/utils"
	"log"
	"time"
)

// type Seed struct {
// 	id             int
// 	video_name     sql.NullString
// 	video_page_url sql.NullString
// 	video_m3u8_url sql.NullString
// 	mp3_path       sql.NullString
// 	srt_path       sql.NullString
// 	video_language sql.NullString
// 	video_no       sql.NullString
// 	video_desc     sql.NullString
// 	create_time    sql.NullString
// 	update_time    sql.NullString
// }

var Db *sql.DB

func InsertSubtitle(seed_id, path, language, format, source, origin_id string) ([]map[string]interface{}, error) {
	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered from ", r)
			return
		}
	}()

	sql := `
	insert into subtitle (seed_id, path, language, format, source, origin_id)
	values ($1,$2,$3,$4,$5,$6)
	`

	result, err := utils.GetAllData(sql, seed_id, path, language, format, source, origin_id)
	if err != nil {
		return nil, err
	}
	return result, nil
}

func InsertSeed(videoNo, videoName, videoPageUrl, videoM3u8Url, mp3Path, srtPath, videoLanguage, videoDesc string) ([]map[string]interface{}, error) {

	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered from ", r)
			return
		}
	}()

	sql := `
	insert into seed (video_no, video_name, video_page_url, video_m3u8_url, mp3_path, srt_path, video_language, video_desc, create_time, process_status, wanttimes)
	values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11) returning id
	`

	result, err := utils.GetAllData(sql, videoNo, videoName, videoPageUrl, videoM3u8Url, mp3Path, srtPath, videoLanguage, videoDesc, time.Now(), "0", 1)
	if err != nil {
		return nil, err
	}
	return result, nil
}

func InsertWant(seed_id, client_ip, want_lang, fullfilled string) error {
	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered from ", r)
			return
		}
	}()

	sql := `
	insert into want (seed_id, client_ip, want_lang,create_time, fullfilled)
	values ($1,$2,$3,$4, $5)
	`

	_, err := utils.GetAllData(sql, seed_id, client_ip, want_lang, time.Now(), fullfilled)
	if err != nil {
		return err
	}
	return nil
}

func UpdateSeed(id, videoNo, videoName, videoPageUrl, videoM3u8Url, mp3Path, srtPath, videoLanguage, videoDesc, process_status, err_msg string) ([]map[string]interface{}, error) {

	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered from ", r)
			return
		}
	}()
	sql := `
	update seed set video_no=$1, video_name=$2, video_page_url=$3, video_m3u8_url=$4, mp3_path=$5, srt_path=$6, video_language=$7, video_desc=$8, update_time = $9 , process_status = $11, err_msg = $12 where id=$10
	`
	result, err := utils.GetAllData(sql, videoNo, videoName, videoPageUrl, videoM3u8Url, mp3Path, srtPath, videoLanguage, videoDesc, time.Now(), id, process_status, err_msg)
	if err != nil {
		return nil, err
	}
	return result, nil
}

func SelectSeed(h string) ([]map[string]interface{}, error) {
	var sql string
	var err error
	var data []map[string]interface{}
	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered from ", r)
			return
		}
	}()
	if len(h) > 0 {
		hint := "%" + h + "%"
		println(hint)
		sql = `
			select * from seed 
			where video_no like $1  
				or video_name like $2  
				or video_page_url like $3  
				or  video_m3u8_url like $4  
				or  mp3_path like $5  
				or  srt_path like $6  
				or  video_language like $7  
				or  video_desc like $8
			`
		println(sql)
		data, err = utils.GetAllData(sql, hint, hint, hint, hint, hint, hint, hint, hint)
	} else {
		sql = `select * from seed`
		data, err = utils.GetAllData(sql)
	}
	if err != nil {
		log.Println(err)
		return nil, err
	}

	return data, nil
}

func SelectSeedNeedProcess(t string) ([]map[string]interface{}, error) {
	var sql string
	var err error
	var data []map[string]interface{}

	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered from ", r)
			return
		}
	}()
	status := "0"
	switch t {
	case "download":
		status = "0"
		sql = `select * from seed 
			where process_status = $1 
			order by client_ip nulls first , process_status, wanttimes desc, create_time 
			limit 1`
	case "transcribe":
		status = "1"
		sql = "select * from seed where process_status = $1 order by process_status, wanttimes desc, create_time limit 1"
	case "translate":
		status = "2"
		//sql = "select * from seed where process_status = $1 or process_status = '3v0' order by process_status, wanttimes desc, create_time limit 1"
		sql = `
			select t1.*, t2.create_time as "want_time" from seed t1
			left join want t2 on t1.id::text = t2.seed_id 
			where process_status =$1 or process_status = '3v0' 
			order by process_status asc, t2.create_time asc nulls last ,wanttimes desc, create_time limit 1
		`
	}

	data, err = utils.GetAllData(sql, status)

	if err != nil {
		log.Println(err)
		return nil, err
	}

	//sql = "update seed set process_status = '1' where id = $1 "
	//utils.GetAllData(sql, data[0]["id"].(int64))

	return data, nil
}

func GetSeedByCondition(pageUrl, m3u8Url, video_name, video_no string) ([]map[string]interface{}, error) {
	var sql string
	var err error
	var data []map[string]interface{}
	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered from ", r)
			return
		}
	}()
	sql = `
		select * from seed where (video_page_url is not null and video_page_url != '' and video_page_url = $1) or (video_m3u8_url is not null and video_m3u8_url != '' and video_m3u8_url = $2) or (video_name is not null and video_name != '' and video_name = $3) or (video_no is not null and video_no != '' and video_no = $4)
		`
	data, err = utils.GetAllData(sql, pageUrl, m3u8Url, video_name, video_no)

	if err != nil {
		log.Println(err)
		return nil, err
	}
	return data, nil
}

func GetSeedByPageUrl(pageUrl, videoNo string) ([]map[string]interface{}, error) {
	var sql string
	var err error
	var data []map[string]interface{}
	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered from ", r)
			return
		}
	}()
	sql = `
		select * 
		from seed 
		where 
			(video_page_url is not null and video_page_url != '' and video_page_url = $1)   
			or (video_no is not null and video_no != '' and $2 ilike video_no || '%')
		`
	data, err = utils.GetAllData(sql, pageUrl, videoNo)

	if err != nil {
		log.Println(err)
		return nil, err
	}
	return data, nil
}
func IncreaseWantTime(id int64) ([]map[string]interface{}, error) {
	sql := "update seed set wanttimes = wanttimes + 1 where id = $1"
	data, err := utils.GetAllData(sql, id)
	if err != nil {
		log.Println(err)
		return nil, err
	}
	return data, nil
}

func GetSubtitle_BySeedIdAndLanguage(id, uuid, subtitleId, language string) ([]map[string]interface{}, error) {

	var sql string
	var data []map[string]interface{}
	var err error
	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered from ", r)
			return
		}
	}()
	if len(language) == 0 {
		sql = `
			select * 
			from subtitle 
			where create_time in (
				select max(create_time) over (partition by seed_id, language, format) 
				from subtitle 
				where seed_id = $1
			)
		`
		data, err = utils.GetAllData(sql, id)
	} else if len(subtitleId) > 0 {
		sql = `
			select * 
			from subtitle
			where id = $1
		`
		data, err = utils.GetAllData(sql, subtitleId)
	} else if len(uuid) > 0 && len(language) > 0 {
		sql = `
			select * 
			from subtitle 
			where seed_id = (
				select id from seed where uuid = $1
			) and language = $2
			order by create_time desc limit 1 
		`
		data, err = utils.GetAllData(sql, id, language)
	} else if len(id) > 0 && len(language) > 0 {
		sql = `
			select * 
			from subtitle 
			where seed_id = $1 and language = $2
			order by create_time desc limit 1 
		`
		data, err = utils.GetAllData(sql, id, language)
	}

	if err != nil {
		log.Println(err)
		return nil, err
	}
	// if len(data) == 0 {
	// 	return nil, nil
	// }
	return data, nil
}

func GetWantsNotProcess(seed_id string) ([]map[string]interface{}, error) {
	sql := `
		select distinct want_lang from want where seed_id = $1
		and ( 
			split_part(want_lang, '&&',1) not in (
			select language from subtitle where seed_id::text = $1 
			)
		)
	`
	data, err := utils.GetAllData(sql, seed_id)
	if err != nil {
		log.Println(err)
		return nil, err
	}
	// if len(data) == 0 {
	// 	return nil, nil
	// }
	return data, nil
}

func WantSeed() ([]map[string]interface{}, error) {
	// sql := `
	// 	select t1.id as "want_id", split_part(t1.want_lang,'&&',1)  as "want_lang" , t2.*
	// 	from want t1
	// 	join seed t2 on t1.seed_id = t2.id::text
	// 	where t1.fullfilled = 'N' and t2.process_status in ('2','3')
	// 	order by t1.create_time
	// 	limit 1
	// `
	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered from ", r)
			return
		}
	}()
	sql := `
	select o_want_id as "want_id", o_want_lang as "want_lang", o_id as "id", o_srt_path as "srt_path", 
	o_video_language as "video_language", o_process_status as "process_status", o_wanttimes as "wanttimes" ,
	o_video_name as "video_name",o_video_page_url as "video_page_url", o_video_m3u8_url as "video_m3u8_url", 
	o_mp3_path as "mp3_path", o_video_no as "video_no", o_video_desc as "video_desc"
	from p_get_want()
	`
	data, err := utils.GetAllData(sql)
	if err != nil {
		log.Println(err)
		return nil, err
	}
	// if len(data) == 0 {
	// 	return nil, nil
	// }
	return data, nil
}

func WangFullfilled(want_id, fullfilled string) ([]map[string]interface{}, error) {
	sql := `
		update want t1
		set fullfilled = $2
		from want t2
		where split_part(t1.want_lang,'&&',1) = split_part(t2.want_lang,'&&',1)
		and t1.seed_id = t2.seed_id
		and t2.id = $1
	`
	data, err := utils.GetAllData(sql, want_id, fullfilled)
	if err != nil {
		log.Println(err)
		return nil, err
	}
	// if len(data) == 0 {
	// 	return nil, nil
	// }
	return data, nil
}

func CheckIfFullfilled(seed_id, lang string) (bool, int) {
	sql := `
		select count(1)
		from subtitle 
		where seed_id = $1
			and language = $2
	`
	data, err := utils.GetAllData(sql, seed_id, lang)
	if err != nil {
		log.Println(err)
		return false, 0
	}
	count := data[0]["count"].(int64)

	sql1 := `
		select count(1)
		from want
		where seed_id = $1
			and want_lang = $2
	`
	data1, err1 := utils.GetAllData(sql1, seed_id, lang)
	if err1 != nil {
		log.Println(err1)
		return false, 0
	}

	count1 := data1[0]["count"].(int64)

	return count > 0, int(count1)

}

func CheckIfWanted(seed_id, lang string) string {
	sql := `
		select count(1)
		from want
		where seed_id = $1
			and split_part(want_lang,'&&',1) = $2
	`
	data, err := utils.GetAllData(sql, seed_id, lang)
	if err != nil {
		log.Println(err)
		return "no"
	}
	count := data[0]["count"].(int64)

	if count > 0 {
		sql = `
		select count(1)
		from want
		where seed_id = $1
			and split_part(want_lang,'&&',1) = $2
			and fullfilled = 'Y'
		`
		data, err = utils.GetAllData(sql, seed_id, lang)
		if err != nil {
			log.Println(err)
			return "no"
		}
		count = data[0]["count"].(int64)
		if count > 0 {
			return "fullfilled"
		}
		return "yes"
	} else {
		return "no"
	}
}

func UpdateSeedProcessstatus(seedId int64, processStatus string) {
	defer func() {
		if r := recover(); r != nil {
			log.Println("Recovered from ", r)
			return
		}
	}()
	sql := `
		update seed set process_status = $1 where seed_id = $2
	`
	utils.GetAllData(sql, processStatus, seedId)
}
