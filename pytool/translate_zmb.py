import gc
import re
from utils import *
import request
import os
import time
import sys
from api_translate import translate
import hashlib

class Unbuffered:
    def __init__(self, stream):
       self.stream = stream

    def write(self, data):
        try:        
            self.stream.write(data)
            self.stream.flush()
            te3.write(data)    # Write the data of stdout here to a text file as well
            te3.flush()
        except Exception as e:
            pass
    
    def flush(data):
        try:
            te3.flush()
        except Exception as e:
            pass

current_directory = os.path.dirname(os.path.abspath(__file__))
te3 = open(current_directory+"/../file/log/subtitle_t2tt.log",'a', encoding='utf-8')  # File where you need to keep the logs
sys.stdout=Unbuffered(sys.stdout)

# Initialize a Translator object with a multitask model, vocoder on the GPU.

#model_name = "seamlessM4T_v2_large"
model_name = "seamlessM4T_medium"
vocoder_name = "vocoder_v2" #if model_name == "seamlessM4T_v2_large" else "vocoder_36langs"

def generate_new_filepath(existing_filepath, after_fix):
    # Split the existing filepath into directory and filename
    directory, filename = os.path.split(existing_filepath)
    # Split the filename into name and extension
    name, extension = os.path.splitext(filename)
    filename = name.split("_")[0]
    # Append "_abc" to the original filename
    new_filename = f"{filename}_{after_fix}{extension}"
    # Join the directory and the new filename to create the new filepath
    new_filepath = os.path.join(directory, new_filename)
    return new_filepath, extension, new_filename

import redis  
# 创建Redis连接对象  
r = redis.Redis(host='192.168.2.203', port=6379, db=0,decode_responses=True)
zmb_pending_subtitle_id = 'zmb_pending_subtitle_id'

def translate_func():
    subtitle_id = r.rpop(zmb_pending_subtitle_id)
    #subtitle_id = '40025'
    subtitle_array = request.GetSubtitleInfo('','',subtitle_id)  #获取源语言
    if subtitle_array is None or len(subtitle_array) == 0:
        print(subtitle_id, " subtitle is None")
        return
    origin_subtitle = subtitle_array[0]
    seed_id = origin_subtitle["seed_id"]
    try:
        LocalPathPrefix = './file/'
        #从服务端拉取原始语言的字幕到本地
        srt_path = origin_subtitle['path']
        request.PullSrtFromServerBySubtitleId(subtitle_id,srt_path,LocalPathPrefix)
        src_path = LocalPathPrefix + srt_path
        video_language = origin_subtitle["language"]
        src_lang = video_language
        uuid = origin_subtitle["uuid"]
        #tgt_langs = ['cmn_Hant','eng','kor','spa','por','swe','deu','arb','rus','fra','ita']
        tgt_langs = ['cmn_Hant','eng','kor']
        for tgt_lang in tgt_langs:
            if tgt_lang == src_lang:
                continue
            print(f"开始subtitle_id:{subtitle_id} {tgt_lang}")
            tgt_path, extension, tgt_filename = generate_new_filepath(src_path, tgt_lang)
            tgt_filename = uuid +"_"+tgt_lang+".srt"
            tgt_path = LocalPathPrefix + tgt_filename
            src_lang = 'auto'
            out_put = translate(src_path, tgt_path, src_lang, tgt_lang) 
            if len(out_put) > 0:
                msg = f"翻译失败，subtitle_id = {subtitle_id}，接口输出报错{out_put}"
                r.lpush('zmb_error_list', subtitle_id)
                print(msg)
                return msg
            subtitle = {}
            file_path = os.path.join('trans/',  tgt_path.replace(LocalPathPrefix, ''))
            subtitle["language"] = tgt_lang
            subtitle["path"] = file_path
            subtitle["seed_id"] = str(origin_subtitle["seed_id"])
            subtitle["format"] = extension
            subtitle['source'] = 'zmb2'
            subtitle['origin_id'] = str(subtitle_id)
            request.PushSubtitleToServer(tgt_path,file_path)            
            request.SaveSubtitle(subtitle)  
        #将seed状态更新为5.1 已翻译eng，cmn_Hant
        request.UpdateSeedStatus(str(seed_id), '5.1')
    except Exception as e:
        print(f"翻译异常{subtitle_id} "+str(e))
        r.lpush(zmb_pending_subtitle_id,subtitle_id)
def doTranslate():
    while True :
        try:
            res = translate_func()
            if res is not None:
                print(res)
                #return
        except Exception as e:
            print(str(e))
        finally:
            time.sleep(2)

doTranslate()