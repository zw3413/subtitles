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

def translate_by_google(enText,sl,tl):  #enText length<5000
    #print(len(enText))
    def resolveGoogle(res):
        j={}
        result=''
        try:
            j=json.loads(res)
        except Exception as e:
            print(str(e))
            print(res)
            #j['sentences']=[]
            result = 'error:' + str(e)
        else:    
            if len(j['sentences'])>0:
                for sentence in j['sentences']:
                    result=result+'\n'+sentence['trans']
                result=result[1:len(result)]    
        return result
    engine=googleEngine % (sl,tl)
    #enText_list=split_text(enText,5000)
    for i in range(3):
        url=engine+enText
        #print(url)
        #headers={'user-agent': 'Mozilla/5.0'}
        headers = {'Cookie':'HSID=An3yVavDXnJsCjJX4; APISID=GbFUPsblEdd9yiZI/AI527FAyf4FINb0vq; SID=g.a000hQj3jVOCCN7Ek-sE52vGKZeIwoXdv8Z8v_kGPw_dL-UPX_B1Ku3G8nvn3bQziVv-sD7HRwACgYKAQQSAQASFQHGX2MiBqKkQKmc-bPZFswg03wcaRoVAUF8yKqGY4hd0hlKb2Y9lCJ79sBz0076; SEARCH_SAMESITE=CgQI3poB; GOOGLE_ABUSE_EXEMPTION=ID=e364c4a9bf89ecb1:TM=1711970932:C=r:IP=104.28.245.199-:S=bMjdCgQgPPS-y7P_2F9Rr3k; SIDCC=AKEyXzUl8lGt0yPWFecqog05uipQCkP2i-ViZDrOySZq-H8LZzrr3Qq02tdXMbo0O1YLA83Tes0c',
                   'Host':'translate.google.com'}
        try:
            res=requests.get(url,headers=headers)
            res.encoding="UTF-8"
            result= resolveGoogle(res.text)
            if not result.startswith('error:'):
                return result
            #result = ''
            print("失败重试"+str(i))
        except Exception as e:
            print(str(e))
            result = "error:"+str(e)
            print("失败重试"+str(i))
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

    tgt_path_tmp = tgt_path + ".tmp"
    if os.path.exists(tgt_path_tmp):
        os.remove(tgt_path_tmp)
    tgt_file_tmp = open(tgt_path_tmp, "w", encoding='utf-8')
    # f.write(segment.text)
    # f.write("\n")
    src_file = open(src_path, "r", encoding = "utf-8")
    try:
        sl = langCode3To2(src_lang)
        tl = langCode3To2(tgt_lang)
        if tl =="yue":
            tl = "zh-tw"
        input = ''
        for line_from_file in src_file:
            line = line_from_file.strip()
            
            if len(line)>200 :
                line = line[0:200]
            input =input + line+"\n"
            if len(input) >1800:
                #print(str(len(input)))
                text_output = translate_by_google(input, sl,tl)
                if text_output.startswith('error:'):
                    #翻译失败
                    return text_output
                tgt_file_tmp.write(text_output)
                tgt_file_tmp.write("\r\n")
                input = ''
        if len(input.strip())>0 :
            #print(str(len(input)))
            text_output = translate_by_google(input, sl,tl)
            if text_output.startswith('error:'):
                #翻译失败
                return text_output
            tgt_file_tmp.write(text_output)

        tgt_file_tmp.flush()
        tgt_file_tmp.close()

        tgt_file_tmp = open(tgt_path_tmp, "r", encoding='utf-8')

        for line_from_file in tgt_file_tmp:
            line = line_from_file.strip()
            # if re.match(pattern_num, line) and line != "1":
            #     tgt_file.write('\n')
            if len(line)==0 or re.match(pattern_timestamp, line):
                tgt_file.write('\n')
            tgt_file.write(line)
        
        tgt_file.close()
        tgt_file_tmp.close()
        os.remove(tgt_path_tmp)

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