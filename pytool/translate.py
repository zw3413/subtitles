import gc
import re
from utils import *
import request
import os
import time
import sys
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
    # Append "_abc" to the original filename
    new_filename = f"{filename}_{after_fix}{extension}"
    # Join the directory and the new filename to create the new filepath
    new_filepath = os.path.join(directory, new_filename)
    return new_filepath, extension, new_filename

def translate_func_v1():
     #如果源语言就是eng，则直接存入subtitle表
    #   获取待翻译seed            
    seeds = request.GetWantSeed()
    if seeds is None or len(seeds) == 0 :
        #print(cmd,"没有待翻译的seed")
        return
    try:
        seed = seeds[0]  
        id = seed["id"]
        seed["id"] = str(id)
        print(cmd,"开始翻译seed："+str(id))
        srt_path = seed["srt_path"]
        src_path = filePath_prefix + srt_path
        video_language = seed["video_language"]
        src_lang = language_codes[video_language]
        process_status = seed["process_status"]
        
        #  #获取want列表
        # wants = request.GetWantsNotProcessed(str(id))
        want = {}
        want["id"] = seed["want_id"]
        want["want_lang"] = seed["want_lang"]
        
        #如果源语言不是eng, 先从源语言翻译为eng, 如果状态未3v* 默认为已经有eng了
        if src_lang != "eng"  and process_status == "2":
            tgt_lang = "eng"
            tgt_path,extension,tgt_filename = generate_new_filepath(src_path, tgt_lang)
            out_put = translate(src_path, tgt_path, src_lang, tgt_lang)  
            if len(out_put) > 0:
                request.PostWantFullfilled(want["id"],out_put)
                return
            subtitle = {}  
            subtitle["language"] = tgt_lang
            subtitle["path"] = tgt_filename
            subtitle["seed_id"] = seed["id"]
            subtitle["format"] = extension
            request.SaveSubtitle(subtitle)
            seed["process_status"] = "3" 
            seed["err_msg"]= ""
            request.SaveSeed(seed)
            if want["want_lang"] == "eng":
                request.PostWantFullfilled(want["id"], "Y")
                return
        if src_lang =="eng" and process_status == "2":
            seed["process_status"] = "3" 
            seed["err_msg"]= ""
            request.SaveSeed(seed)
            if want["want_lang"] == "eng":
                request.PostWantFullfilled(want["id"], "Y")
                return
        
        want_lang = want["want_lang"]
        if want_lang != "eng":
            #获取eng源srt
            src_lang_eng = "eng"
            result = request.GetSubtitleInfo(id,src_lang_eng)
            if len(result)==0 :
                request.PostWantFullfilled(want["id"],"E,didn't find eng") 
                return
            subtitle = result[0]
            srt_path = subtitle["path"]
            src_path = filePath_prefix+srt_path 
            tgt_lang = want_lang
            tgt_path, extension, tgt_filename = generate_new_filepath(src_path, tgt_lang)
            
            out_put = translate(src_path, tgt_path, src_lang_eng, tgt_lang) 
            if len(out_put) > 0:
                request.PostWantFullfilled(want["id"],out_put)
                return
            subtitle = {}
            subtitle["language"] = tgt_lang
            subtitle["path"] = tgt_filename
            subtitle["seed_id"] = seed["id"]
            subtitle["format"] = extension
            request.SaveSubtitle(subtitle)  
            request.PostWantFullfilled(want["id"],'Y') 
        else:
            request.PostWantFullfilled(want["id"], "Y")
            return
    except Exception as e:
        print(cmd,"翻译异常"+str(e))
        #seed["process_status"] = "3e"
        #seed["err_msg"] = cmd + "翻译异常" + str(e)
        #request.SaveSeed(seed)


def translate_func_v2():
     #如果源语言就是eng，则直接存入subtitle表
    #   获取待翻译seed            
    seeds = request.GetWantSeed()
    if seeds is None or len(seeds) == 0 :
        #print(cmd,"没有待翻译的seed")
        return
    seed = seeds[0] 
    try:
        id = seed["id"]
        seed["id"] = str(id)
        print(cmd,"开始翻译seed："+str(id))
        srt_path = seed["srt_path"]
        src_path = filePath_prefix + srt_path
        video_language = seed["video_language"]
        src_lang = language_codes[video_language]
        tgt_lang = seed["want_lang"]
        tgt_path, extension, tgt_filename = generate_new_filepath(src_path, tgt_lang)
        out_put = translate(src_path, tgt_path, src_lang, tgt_lang) 
        if len(out_put) > 0:
            request.PostWantFullfilled(seed["want_id"],out_put)
            #print(out_put)
            return
        subtitle = {}
        subtitle["language"] = tgt_lang
        subtitle["path"] = tgt_filename
        subtitle["seed_id"] = seed["id"]
        subtitle["format"] = extension
        request.SaveSubtitle(subtitle)  
        request.PostWantFullfilled(seed["want_id"],'Y') 
        seed["process_status"] = "3" 
        seed["err_msg"]= ""
        request.SaveSeed(seed)
    except Exception as e:
        print(cmd,"翻译异常"+str(e))
        request.PostWantFullfilled(seed["want_id"],str(e)) 


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
        src_lang = language_codes[video_language]
        tgt_lang = seed["want_lang"]
        tgt_path, extension, tgt_filename = generate_new_filepath(src_path, tgt_lang)
        out_put = translate(src_path, tgt_path, src_lang, tgt_lang) 
        if len(out_put) > 0:
            request.PostWantFullfilled(seed["want_id"],out_put)
            #print(out_put)
            return
        subtitle = {}
        subtitle["language"] = tgt_lang
        subtitle["path"] = tgt_filename
        subtitle["seed_id"] = seed["id"]
        subtitle["format"] = extension
        subtitle['source'] = '2'
        request.PushSubtitleToServer(tgt_path,tgt_filename)
        
        request.SaveSubtitle(subtitle)  
        request.PostWantFullfilled(seed["want_id"],'Y') 
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