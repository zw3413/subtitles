import os
import re
import hashlib
import request
import time
import utils
import sys
from faster_whisper import WhisperModel
import torch
from datetime import timedelta, datetime
#from translate import translate_func

class Unbuffered:
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        try:        
            self.stream.write(data)
            self.stream.flush()
            te2.write(data)    # Write the data of stdout here to a text file as well
            te2.flush()
        except Exception as e:
            pass
    
    def flush(data):
        try:
            te2.flush()
        except Exception as e:
            pass

filePath_prefix = '../file/subtitle/'
video_filePath_prefix = 'F:\\abc\\'
MP3_afterfix = '.mp3'
SRT_afterfix = '.srt'
FLV_afterfix = '.flv'

current_directory = os.path.dirname(os.path.abspath(__file__))
te2 = open(current_directory+"/../file/log/subtitle_transcribe.log",'a', encoding='utf-8')  # File where you need to keep the logs
sys.stdout=Unbuffered(sys.stdout)



device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)
compute_type = "float16" if torch.cuda.is_available() else "int8"
#model_size = 'large-v3' # "base" # 
model_size = 'large-v2'
#model_size = 'distil-large-v2'
#model_size = 'zh-plus/faster-whisper-large-v2-japanese-5k-steps' #https://huggingface.co/zh-plus/faster-whisper-large-v2-japanese-5k-steps
#model_size = 'base'
print("start to init WhisperModel")
t1 = time.time()
model = WhisperModel(
    model_size, 
    device = device , 
    compute_type= compute_type, 
    local_files_only = False,
    #flash_attention=True
)
print("finished init WhisperModel")
t2 = time.time()
te = t2 - t1
print(f"完成耗时 {te:.6f} seconds")
def transcribe_func() :
    cmd = "transcribe"
    start_time = time.time()
    try:
        #print(cmd,"获取待转文字的seed")
        seeds = request.GetNextNeedProcessSeed("transcribe")
        if seeds is None or len(seeds) == 0 :
            #print(cmd,"没有待转文字的seed")
            return
        seed = seeds[0]  
        id = seed["id"]
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

        #prompt = "Japanese adult video subtitles: Capture nuances, emotions accurately. Use appropriate language, tone. Consider: 1. Contextual understanding. 2. Emotional tone. 3. Cultural sensitivity. 4. Clarity, readability, synchronization. Example: casual conversation, intimate dialogue."
        prompt_e = "Generate subtitle for this Japanese adult video: Capture nuances, emotions, and context accurately with appropriate language and tone,  synchronization with audio."
        prompt_j = "この日本のアダルト ビデオの字幕を生成します。適切な言語とトーン、オーディオとの同期で、ニュアンス、感情、コンテキストを正確に捉えます。"
        vad = dict(threshold = 0.4, min_speech_duration_ms=300, max_speech_duration_s=30, min_silence_duration_ms=200, speech_pad_ms=150 )

        segments, info = model.transcribe(
            video_filePath_prefix+flvPath, 
            beam_size=5, 
            vad_filter=True, 
            #vad_parameters= vad,
            initial_prompt = prompt_j,
            task = "transcribe"
            )
        
        print(cmd,"Detected language '%s' with probability %f" % (info.language, info.language_probability))
        if info.language_probability < 0.8 and info.language != 'ja': #如果语言预测的可能性小于0.9，强制使用ja
            segments, info = model.transcribe(
                video_filePath_prefix+flvPath, 
                beam_size=5, 
                vad_filter=True, 
                #vad_parameters=vad,
                language="ja",
                initial_prompt = prompt_j,
                task = "transcribe"
                )
            print(cmd,"Detected language '%s' with probability %f" % (info.language, info.language_probability))
        language = info.language
        #srtPath = filePath.split('.')[0]+ info.language + '.srt'
        srtPath = filePath_prefix + flvPath.replace(MP3_afterfix,SRT_afterfix).replace(FLV_afterfix, SRT_afterfix).replace('_worst','').replace('_best','')
            #delete the file at filePath if exist
        if os.path.exists(srtPath):
            os.remove(srtPath)
        f = open(srtPath, "w", encoding='utf-8')
        #print(cmd,srtPath)
        lineCount = 0
        t_start = datetime.now()
        pt = ''
        for segment in segments :
            lineCount += 1
            f.write(str(lineCount)+"\n")
            s = utils.secondsToStr(segment.start)
            e = utils.secondsToStr(segment.end)
            f.write( s + ' --> ' + e +"\n")
            t = e.split(",",1)[0].replace(":","")[0:3]
            if t != pt:
                print(t, end=" ")
                pt= t
            #print("write segment text")
            #str_content = str(segment.text.encode('gbk'),encoding = 'utf-8')
            f.write(segment.text)
            f.write("\n\n")
            #print(segment.text)
            lineCount = lineCount + 1
        f.flush()
        f.close()
        file_name =  srtPath.replace(filePath_prefix,"")
        request.PushSubtitleToServer(srtPath, file_name)
        seed["srt_path"] =file_name
        seed["video_language"] = language
        seed["process_status"] = "2"
        seed["transcribe_version"] = '24.07.11-l'
        seed["err_msg"]= ""
        seed["transcribe_version"] = "24.07.11"
        request.SaveSeed(seed)
        subtitle = {}
        subtitle["language"] = utils.language_codes[language]
        subtitle["path"] = srtPath.replace(filePath_prefix,"")
        subtitle["seed_id"] = seed["id"]
        subtitle["format"] = SRT_afterfix
        subtitle["source"] = '1'
        request.SaveSubtitle(subtitle)
        
    except Exception as e:
        
        
        print(cmd,"字幕生成失败")
        print(e)
        seed["process_status"] = "2e"
        seed["err_msg"] = cmd + "字幕生成失败" + str(e)
        request.SaveSeed(seed)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"完成耗时 {elapsed_time:.6f} seconds")

    
def transcribe():
    while True:
        try:
            transcribe_func()
            #translate_func()
        finally:
            time.sleep(5)
    
transcribe()
