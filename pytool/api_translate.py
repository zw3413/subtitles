#!/usr/bin/env python
#coding=utf-8
import time
import json
import requests
import os
import re
from utils import *

#目前可以使用的翻译方法有：
# translate_by_ali      yes,支持text和html
# translate_by_google   yes,支持text和html
# translate_by_youdao   频繁调用会被封,仅支持text
# translate_by_bing     需要申请azure的试用key

googleEngine='http://translate.google.com/translate_a/single?client=gtx&dt=t&dj=1&ie=UTF-8&sl=%s&tl=%s&q='

def translate_by_google(enText,sl,tl):
    def resolveGoogle(res):
        j={}
        result=''
        try:
            j=json.loads(res)
        except:
            print('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
            print(res)
            j['sentences']=[]    
        else:    
            if len(j['sentences'])>0:
                for sentence in j['sentences']:
                    result=result+'\n'+sentence['trans']
                result=result[1:len(result)]    
        return result
    engine=googleEngine % (sl,tl)
    enText_list=split_text(enText,5000)
    result=''
    for t in enText_list:
        if(t is not None and len(t)>0):
            url=engine+t
            headers={'user-agent': 'Mozilla/5.0'}
            res=requests.get(url,headers=headers)
            res.encoding="UTF-8"
            result= result+resolveGoogle(res.text)
    return result


cmd ="translate"

def translate(src_path, tgt_path, src_lang, tgt_lang) :
    start_time = time.time()
    print(tgt_lang+" "+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    if src_path is None or src_path == "":
        print(cmd,"srtPath is empty")
        return cmd + "srtPath is empty"
            
    if os.path.exists(tgt_path):
        os.remove(tgt_path)
    tgt_file = open(tgt_path, "w", encoding='utf-8')
    # f.write(segment.text)
    # f.write("\n")
    src_file = open(src_path, "r", encoding = "utf-8")
    try:
        for line_from_file in src_file:
            line = line_from_file.strip()
            if re.match(pattern_num, line) or re.match(pattern_timestamp, line):
                tgt_file.write(line+"\n")
            elif len(line) == 0 :
                tgt_file.write("\n")
            else:        
                sl = langCode3To2(src_lang)
                tl = langCode3To2(tgt_lang)
                text_output=translate_by_google(line,sl, tl)
                # text_output, _ = translator.predict(
                #     input = line,
                #     task_str="t2tt",
                #     tgt_lang=tgt_lang,
                #     src_lang=src_lang,
                # )
                tgt_file.write(f"{text_output[0]}\n")
                #print(f"{tgt_lang}: {text_output_en[0]}")
        return ""    
    except Exception as e:
        return str(e)
    finally:

        tgt_file.close()
        src_file.close()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"完成耗时 {elapsed_time:.6f} seconds")

if(__name__=='__main__'):
    enText="<a>Hello, my dear.</a>"
    zhText=translate_by_google(enText)
    print(zhText)