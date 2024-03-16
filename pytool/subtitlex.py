import os
import re
import hashlib
import request
import time
import utils
import torch
from threading import Thread
from faster_whisper import WhisperModel
from datetime import  datetime
from seamless_communication.inference import Translator

filePath_prefix = '../file/subtitle/'
#filePath_prefix = '/content/file/subtitle/'
MP3_afterfix = '.mp3'
SRT_afterfix = '.srt'
FLV_afterfix = '.flv'

pattern_num = r'^-?\d+$' #regx pattern of No. 
pattern_timestamp = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$') #regx pattern of timestamp

tgt_langs = ("cmn","cmn_Hant","spa","por","swe","deu","arb","rus","fra","jpn")

device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)
compute_type = "float16" if torch.cuda.is_available() else "int8"
model_size = 'large-v3' # "base" # 
model = WhisperModel(
    model_size, 
    device = device , 
    compute_type= compute_type, 
    local_files_only = False,
)

#model_name = "seamlessM4T_v2_large"
model_name = "seamlessM4T_medium"
vocoder_name = "vocoder_v2" #if model_name == "seamlessM4T_v2_large" else "vocoder_36langs"

translator = Translator(
    model_name,
    vocoder_name,
    device=torch.device("cuda:0"),
    dtype=torch.float16,
)

#命令行的方式使用streamlink下载视频
def downloadFlv(url,  quality = 'worst'):
    threads = '2'
    quality = quality # "worst"
    afterfix = FLV_afterfix
    fileName =  hashlib.md5(url.encode()).hexdigest() +afterfix
    match = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", url)
    if match != None:
        fileName = match.group(0)+afterfix
    filePath = filePath_prefix + fileName
    #delete the file at filePath if exist
    if os.path.exists(filePath):
        os.remove(filePath)
    if str.lower('youtube.com') in url:
        cmd = 'streamlink --retry-max 10 --stream-segment-timeout 60 --stream-timeout 180 --http-timeout 60 --stream-segment-threads '+threads+' -o "'+filePath+'" --http-header "User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 AOL/9.8 AOLBuild/4346.2019.US Safari/537.36"  '+ url +' '+quality
    else:
        cmd = 'streamlink --retry-max 10 --stream-segment-timeout 60 --stream-timeout 180 --http-timeout 60 --stream-segment-threads '+threads+' -o "'+filePath+'" --http-header "User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 AOL/9.8 AOLBuild/4346.2019.US Safari/537.36" --http-header "Referer=" "hlsvariant://'+ url +'" '+quality
    print(cmd)
    output = os.system(cmd)
    return output,fileName 
   
def download_func():
    cmd ="download"
    seeds = request.GetNextNeedProcessSeed("download")
    # if the json array seeds length is zero, then stop the precess
    if seeds is None or len(seeds) == 0 :
        #print(cmd,"没有待下载的seed")
        return
    seed = seeds[0]  
    try:
        id = seed["id"]
        seed["id"] = str(id)
        print(cmd,"开始下载seed："+str(id))
        video_m3u8_url = seed["video_m3u8_url"]
        output, flvPath = downloadFlv(video_m3u8_url)
        if output != 0:
            print(cmd,"下载失败")
            seed["process_status"] = "1e"
            seed["err_msg"] = cmd + "下载失败"+str(output)
            request.SaveSeed(seed)
            return
        seed["mp3_path"] = flvPath
        seed["process_status"] = "1"
        seed["err_msg"]= ""
        request.SaveSeed(seed)
        print(cmd,"下载完成")
    except Exception as e:
        print(cmd,"下载异常"+str(e))
        print(e)
        seed["process_status"] = "1e"
        seed["err_msg"] = cmd + "下载异常" + str(e)
        request.SaveSeed(seed)

def transcribe_func() :
    cmd = "transcribe"
    try:
        #print(cmd,"获取待转文字的seed")
        seeds = request.GetNextNeedProcessSeed("transcribe")
        if seeds is None or len(seeds) == 0 :
            #print(cmd,"没有待转文字的seed")
            return
        seed = seeds[0]  
        id = seed["id"]
        start_time = time.time()
        print(str(id)+" "+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        seed["id"] = str(id)
        flvPath = seed["mp3_path"]
        if flvPath is None or flvPath == "":
            print(cmd,"flvPath is empty")
            seed["process_status"] = "2e"
            seed["err_msg"] = cmd + "flvPath is empty"
            request.SaveSeed(seed)
            return
        #flvPath = filePath_prefix +"d131749d-18e2-42fe-ad5e-382131f5cf4b.flv"
        #fast-whisper
       
        segments, info = model.transcribe(filePath_prefix+flvPath, beam_size=5, vad_filter=True, task = "transcribe")
        language = info.language
        #print(cmd,"Detected language '%s' with probability %f" % (language, info.language_probability))
        #srtPath = filePath.split('.')[0]+ info.language + '.srt'
        srtPath = filePath_prefix + flvPath.replace(MP3_afterfix,SRT_afterfix).replace(FLV_afterfix, SRT_afterfix).replace('_worst','').replace('_best','')
            #delete the file at filePath if exist
        if os.path.exists(srtPath):
            os.remove(srtPath)
        f = open(srtPath, "w", encoding='utf-8')
        #print(cmd,srtPath)
        lineCount = 1
        t_start = datetime.now()
        for segment in segments :
            #print("write linecount")
            f.write(str(lineCount)+"\n")
            #print(str(lineCount))
            s = utils.secondsToStr(segment.start)
            e = utils.secondsToStr(segment.end)
            f.write( s + ' --> ' + e +"\n")
            print(e.split(",",1)[0].replace(":",""), end=" ")
            #print("write segment text")
            #str_content = str(segment.text.encode('gbk'),encoding = 'utf-8')
            f.write(segment.text)
            f.write("\n")
            #print(segment.text)
            lineCount = lineCount + 1
        f.flush()
        f.close()
        seed["srt_path"] = srtPath.replace(filePath_prefix,"")
        seed["video_language"] = language
        seed["process_status"] = "2"
        seed["err_msg"]= ""
        request.SaveSeed(seed)
        subtitle = {}
        subtitle["language"] = utils.language_codes[language]
        subtitle["path"] = srtPath.replace(filePath_prefix,"")
        subtitle["seed_id"] = seed["id"]
        subtitle["format"] = SRT_afterfix
        request.SaveSubtitle(subtitle)
    except Exception as e:
        print(cmd,"字幕生成失败")
        print(e)
        seed["process_status"] = "2e"
        seed["err_msg"] = cmd + "字幕生成失败" + str(e)
        request.SaveSeed(seed)
    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"完成耗时 {elapsed_time:.6f} seconds")

def translate(src_path, tgt_path, src_lang, tgt_lang) :
    cmd ="translate"
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
                #print(f"{tgt_lang}:{line}")
            elif len(line) == 0 :
                tgt_file.write("\n")
            else:        
                text_output, _ = translator.predict(
                    input = line,
                    task_str="t2tt",
                    tgt_lang=tgt_lang,
                    src_lang=src_lang,
                )
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

def t2tt_func():
    cmd="t2tt_func"
     #如果源语言就是eng，则直接存入subtitle表
    #   获取待翻译seed
    try:
        seeds = request.GetNextNeedProcessSeed("translate")
        # if the json array seeds length is zero, then stop the precess
        if seeds is None or len(seeds) == 0 :
            #print(cmd,"没有待翻译的seed")
            return
        seed = seeds[0]  
        id = seed["id"]
        seed["id"] = str(id)
        print(cmd,"开始翻译seed："+str(id))
        video_m3u8_url = seed["video_m3u8_url"]
        srt_path = seed["srt_path"]
        src_path = filePath_prefix + srt_path
        video_language = seed["video_language"]
        src_lang = utils.language_codes[video_language]
        process_status = seed["process_status"]
        
         #获取want列表
        wants = request.GetWantsNotProcessed(str(id))
        
        #如果源语言不是eng, 先从源语言翻译为eng, 如果状态未3v* 默认为已经有eng了
        if src_lang != "eng"  and process_status == "2":
            tgt_lang = "eng"
            tgt_path,extension,tgt_filename = generate_new_filepath(src_path, tgt_lang)
            out_put = translate(src_path, tgt_path, src_lang, tgt_lang)  
            if len(out_put)>0:
                seed["process_status"] = "3e"
                seed["err_msg"] = out_put
                request.SaveSeed(seed)
                return
            subtitle = {}  
            subtitle["language"] = tgt_lang
            subtitle["path"] = tgt_filename
            subtitle["seed_id"] = seed["id"]
            subtitle["format"] = extension
            request.SaveSubtitle(subtitle)   
        
        #获取eng源srt
        src_lang_eng = "eng"
        subtitle = request.GetSubtitleInfo(id,src_lang_eng)[0]
        srt_path = subtitle["path"]
        src_path = filePath_prefix+srt_path 

        if len(wants) > 0 :
            for want in wants :
                want_lang = want["want_lang"]
                if want_lang != "eng":
                    tgt_lang = want_lang
                    tgt_path, extension, tgt_filename = generate_new_filepath(src_path, tgt_lang)
                    out_put = translate(src_path, tgt_path, src_lang_eng, tgt_lang) 
                    if len(out_put)>0:
                        seed["process_status"] = "3e"
                        seed["err_msg"] = out_put
                        request.SaveSeed(seed)
                        return
                    subtitle = {}
                    subtitle["language"] = tgt_lang
                    subtitle["path"] = tgt_filename
                    subtitle["seed_id"] = seed["id"]
                    subtitle["format"] = extension
                    request.SaveSubtitle(subtitle)   
            seed["process_status"] = "3v0" #还未处理第一版
            seed["err_msg"]= ""
            request.SaveSeed(seed)
            print(cmd,"字幕翻译完成3v0,seed id = "+seed["id"])
            
        else :             
            #如果没有未处理wants,直接从eng翻译为第一版语言列表
            for tgt_lang in tgt_langs :
                if tgt_lang != src_lang and tgt_lang != "eng" :
                    tgt_path, extension, tgt_filename = generate_new_filepath(src_path, tgt_lang)
                    out_put = translate(src_path, tgt_path, src_lang_eng, tgt_lang) 
                    if len(out_put)>0:
                        seed["process_status"] = "3e"
                        seed["err_msg"] = out_put
                        request.SaveSeed(seed)
                        return
                    subtitle = {}
                    subtitle["language"] = tgt_lang
                    subtitle["path"] = tgt_filename
                    subtitle["seed_id"] = seed["id"]
                    subtitle["format"] = extension
                    request.SaveSubtitle(subtitle)     
            seed["process_status"] = "3v1"
            seed["err_msg"]= ""
            request.SaveSeed(seed)
            print(cmd,"字幕翻译完成3v1,seed id = "+seed["id"])
        
    except Exception as e:
        print(cmd,"翻译异常"+str(e))
        print(e)
        seed["process_status"] = "3e"
        seed["err_msg"] = cmd + "翻译异常" + str(e)
        request.SaveSeed(seed)

def download():
    while True:
        try:
            download_func()
        finally:
            time.sleep(2)

def transcribe():
    while True:
        try:
            transcribe_func()
        finally:
            time.sleep(2)

def t2tt():
    while True :
        try:
            t2tt_func()
        finally:
            time.sleep(2)
            
def run():
   Thread(target=download).start()
   Thread(target=transcribe).start()
   t2tt()