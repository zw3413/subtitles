import gc
import re
from utils import *
import request
import os
import time
import sys
import hashlib
from api_translate import translate

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
    if len(filename) == 8:
        filename = hashlib.md5(existing_filepath.encode()).hexdigest()
    # Append "_abc" to the original filename
    new_filename = f"{filename}_{after_fix}{extension}"
    # Join the directory and the new filename to create the new filepath
    new_filepath = os.path.join(directory, new_filename)
    return new_filepath, extension, new_filename

def translate_func():
    #如果源语言就是eng，则直接存入subtitle表
    #   获取待翻译seed            
    seeds = request.GetWantSeed()
    if seeds is None or len(seeds) == 0 or seeds[0]["id"] == 0:
        #print(cmd,"没有待翻译的seed")
        return
    seed = seeds[0] 
    try:
        id = seed["id"]
        seed["id"] = str(id)
        print(cmd,"开始翻译seed："+str(id))
        
        LocalPathPrefix = './file/'
        #从服务端拉取原始语言的字幕到本地
        request.PullSrtFromServer(seed,LocalPathPrefix)
        
        srt_path = seed["srt_path"]
        src_path = LocalPathPrefix + srt_path
        video_language = seed["video_language"]
        if video_language is not None and len(video_language) > 0 :
            src_lang = language_codes[video_language]
        else :
            src_lang = 'auto'
        tgt_lang = seed["want_lang"]
        tgt_path, extension, tgt_filename = generate_new_filepath(src_path, tgt_lang)
        result = []
        out_put = translate(src_path, tgt_path, src_lang, tgt_lang, result) 
        #翻译失败
        if len(out_put) > 0:
            request.PostWantFullfilled(seed["want_id"],out_put)
            print(out_put)
            return
        words_num = 0
        duration = 0 
        file_size = 0
        if len(result) == 3 :
            [words_num, duration,file_size] = result
        
        #构建subtitle对象，存入数据库
        subtitle = {}
        subtitle["language"] = tgt_lang
        subtitle["path"] = tgt_filename
        subtitle["seed_id"] = seed["id"]
        subtitle["format"] = extension
        subtitle['source'] = '2'
        subtitle["words_num"] = words_num
        subtitle["duration"] = duration
        subtitle["file_size"] = file_size
        request.PushSubtitleToServer(tgt_path,tgt_filename)
        request.SaveSubtitle(subtitle)  
        
        #更新want表
        request.PostWantFullfilled(seed["want_id"],'Y') 
        
        #更新seed表
        if seed["process_status"] == "8" or seed["process_status"] == "9" :
            seed["process_status"] = "9" 
        else :
            seed["process_status"] = "3"    
        seed["err_msg"]= ""
        request.SaveSeed(seed)

    except Exception as e:
        print(cmd,"翻译异常"+str(e))
        request.PostWantFullfilled(seed["want_id"],str(e)) 

def doTranslate():
    while True :
        try:
            translate_func()
        finally:
            time.sleep(2)

doTranslate()