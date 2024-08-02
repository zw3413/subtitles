--limitation限制
select distinct subtitle_uuid
	from subtitle_log 
	where email = 'zhangweicalm@gmail.com'
and type = 'subtitle'
and created_at > now() - interval '24 hour' 

--高优先级处理
select count(1) from seed where wanttimes >=100 and process_status in ('0','1','1e') and video_no is not null and video_no != '' 
--order by id desc


--待下载
select * from seed 
where process_status = '0' and (video_m3u8_url is not null and video_m3u8_url != '') 
order by client_ip nulls first , process_status, wanttimes desc, create_time 

--待转译
select * from seed where process_status = '1' order by process_status, wanttimes desc, create_time



-- downLoad+transcribe 类型的待处理
select * from seed 
where process_status = '7' 
order by client_ip nulls first , process_status, wanttimes desc, create_time  

--colab 执行的seed
select * from seed where  process_status in ('8','9','7','7e','8e','9e','7.1') order by id

select * from seed where process_status in ('7.1')

select * from seed where id between 254701  and 255001 and process_status  = '0'

select * from subtitle s where seed_id in (
	select id from seed where process_status in ('8','9','7','7e','8e','9e')
)  order by seed_id 


--可用字幕统计
select * from (
select 1 as "no", '6-字幕包已翻译' as "type", count(1) from seed where process_status = '6' --756
union all
select 2 as "no", '5.1-字幕包翻译' as "type", count(1) from seed where process_status = '5.1' --18467
union all
select 3 as "no", '5-字幕包待翻译' as "type", count(1) from seed where process_status = '5' --1603
union all
select 4 as "no", '3-AI已翻译' as "type", count(1) from seed where process_status in ('3','9') --1830  1937  2057
union all
select 5 as "no", '2-AI已转文本' as "type", count(1) from seed where process_status in ('2','8') --83     63    1 
union all
select 6 as "no", '1-AI已下载' as "type", count(1) from seed where process_status = '1' --12     19    9
union all
select 7 as "no", '2e-转文本失败' as "type", count(1) from seed where process_status = '2e' --83     63    1 
union all
select 8 as "no", '1e-下载失败' as "type", count(1) from seed where process_status = '1e' --12     19    9
union all
select 9 as "no", '0-待处理' as "type", count(1) from seed where process_status = '0'
)a order by no

--待翻译异常
SELECT x.* FROM public.want x
WHERE fullfilled not in ('Y','N','mime')

--待翻译
select t1.id, t2.id as seed_id ,split_part(t1.want_lang,'&&',1) , t2.id, t2.srt_path, t2.video_language, t2.process_status, t2.wanttimes,
t2.video_name,t2.video_page_url, t2.video_m3u8_url, t2.mp3_path, t2.video_no, t2.video_desc
from want t1
join seed t2 on t1.seed_id = t2.id::text
where t1.fullfilled = 'N' and t2.process_status in ('2','3','8','9')
order by t1.create_time	


--download 失败
select * from seed where process_status = '1e' order by id desc


--手动插入want
--INSERT INTO want ( seed_id, client_ip, want_lang,  fullfilled)
values --( v_seed_id, i_ip, 'cmn_Hant', 'N'),
	( v_seed_id, i_ip, 'eng', 'N')
	--,( v_seed_id, i_ip, 'spa', 'N')
	--,( v_seed_id, i_ip, 'por', 'N')
	--,( v_seed_id, i_ip, 'swe', 'N')
	--,( v_seed_id, i_ip, 'deu', 'N')
	--,( v_seed_id, i_ip, 'arb', 'N')
	--,( v_seed_id, i_ip, 'rus', 'N')
	,( v_seed_id, i_ip, 'fra', 'N')
	;

select t1.id from seed t1
left join subtitle t2 on t1.id = t2.seed_id and t2."language" = 'eng'
where t2."path" is null

insert into want ( seed_id, client_ip, want_lang,  fullfilled)
select t1.id, null, 'fra','N' from seed t1
left join subtitle t2 on t1.id = t2.seed_id and t2."language" = 'fra'
left join want t3 on t1.id::text = t3.seed_id and t3.want_lang = 'fra'
where t2."path" is null 
and t3.create_time is null

--查询重复seed
select * from (
	select replace(video_no,'-uncensored-leak',''), count(1) from seed 
	group by replace(video_no,'-uncensored-leak','')
) t where t.count >1


--创建字幕包执行批次
 update zmb_subtitle set deal_batch = '1' 
 where video_no_index in (
 	select lower(replace(replace(replace(video_no,'-',''),'_',''),' ','') )
 	from seed
 )
 
 --更新字幕包video_no_index 
  update zmb_subtitle set video_no_index = lower(replace(replace(replace(video_no,'-',''),'_',''),' ','') )
  
-- 更新seed表的video_no_index
  update seed set video_no_index  = lower(replace(replace(replace(replace(video_no,'-uncensored-leak',''),'-',''),'_',''),' ','') )
  
  
--检查重复video_no_index
  select s.video_no, s.video_name, s.video_page_url, s.process_status, s.id, s.create_time, s.update_time, a.video_no_index, a.count 
from seed s
join (
select video_no_index, count from (
	select video_no_index , count(1)
	from seed s 
	group by video_no_index 
)a where a.count>1 ) a on s.video_no_index = a.video_no_index 
and position('_' in s.video_no)>0
order by s.video_no_index,s.video_no

--生成sitemap
select 
	'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' ||
	array_to_string( 
		array(
			select 
				xmlelement(
					name url, 
					xmlforest('https://www.subtitlex.xyz/result/detail/' || uuid as loc, to_char(create_time, 'YYYY-MM-DDThh:mm:ss+08:00') AS lastmod)
				)  ::text
			from subtitle 
			where id between 0 and 100000
		),'') 
	|| '</urlset>'

--拼接语言对象
	select '{' || 'name : "' ||name || '", code : "' || code ||'"},' from "language" l 
