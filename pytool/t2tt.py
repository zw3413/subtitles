import torch, gc
import re
import utils
import request
import os
import time
import sys
from seamless_communication.inference import Translator

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



filePath_prefix = '../file/subtitle/'
cmd = "translate"
pattern_num = r'^-?\d+$' #regx pattern of No. 
pattern_timestamp = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$') #regx pattern of timestamp

tgt_langs = ("cmn","cmn_Hant","spa","por","swe","deu","arb","rus","fra","jpn")

def translate(src_path, tgt_path, src_lang, tgt_lang,translator) :
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
     #如果源语言就是eng，则直接存入subtitle表
    #   获取待翻译seed        
    #seeds = request.GetNextNeedProcessSeed("translate")
    # if the json array seeds length is zero, then stop the precess
    
    seeds = request.GetWantSeed()
    if seeds is None or len(seeds) == 0 :
        #print(cmd,"没有待翻译的seed")
        return
    print("start to init Translator")
    t1 = time.time()
    translator = Translator(
        model_name,
        vocoder_name,
        device=torch.device("cuda:0"),
        dtype=torch.float16,
    )
    print("finished to init Translator")
    t2 = time.time()
    te = t2 - t1
    print(f"完成耗时 {te:.6f} seconds")
    try:
        seed = seeds[0]  
        id = seed["id"]
        seed["id"] = str(id)
        print(cmd,"开始翻译seed："+str(id))
        srt_path = seed["srt_path"]
        src_path = filePath_prefix + srt_path
        video_language = seed["video_language"]
        src_lang = utils.language_codes[video_language]
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
            out_put = translate(src_path, tgt_path, src_lang, tgt_lang, translator)  
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
            out_put = translate(src_path, tgt_path, src_lang_eng, tgt_lang, translator) 
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
        #print(cmd,"字幕翻译完成,seed id = "+str(seed["id"]) +" want_id="+ str(want["id"]) +" want_lang="+want["lang"] )
            
         
        #如果没有未处理wants,直接从eng翻译为第一版语言列表
        # for tgt_lang in tgt_langs :
        #     if tgt_lang != src_lang and tgt_lang != "eng" :
        #         tgt_path, extension, tgt_filename = generate_new_filepath(src_path, tgt_lang)
        #         out_put = translate(src_path, tgt_path, src_lang_eng, tgt_lang) 
        #         if len(out_put)>0:
        #             seed["process_status"] = "3e"
        #             seed["err_msg"] = out_put
        #             request.SaveSeed(seed)
        #             return
        #         subtitle = {}
        #         subtitle["language"] = tgt_lang
        #         subtitle["path"] = tgt_filename
        #         subtitle["seed_id"] = seed["id"]
        #         subtitle["format"] = extension
        #         request.SaveSubtitle(subtitle)     
        # seed["process_status"] = "3v1"
        # seed["err_msg"]= ""
        # request.SaveSeed(seed)
        # print(cmd,"字幕翻译完成3v1,seed id = "+seed["id"])
    except Exception as e:
        print(cmd,"翻译异常"+str(e))
        #seed["process_status"] = "3e"
        #seed["err_msg"] = cmd + "翻译异常" + str(e)
        #request.SaveSeed(seed)
    finally:
        del translator
        gc.collect()
        torch.cuda.empty_cache()



def t2tt():
    while True :
        try:
            t2tt_func()
        finally:
            time.sleep(2)
            
            


# def test():
#     src_path = filePath_prefix+"6eabae01-fd63-4e89-914b-0e8ecee3a65c.srt"
#     tgt_path = filePath_prefix+"6eabae01-fd63-4e89-914b-0e8ecee3a65c_eng1.srt"
#     src_lang ="jpn"
#     tgt_lang ="eng"
#     translate(src_path, tgt_path, src_lang, tgt_lang)
    
# test()



#第一版语言列表： status = 3v1 
#                  seamlessm4t_code    whisper
# 1. 英语(主要语言)     eng             en     
# 2. 中文(繁体)         cmn             zh(yue)
# 3. 西班牙语           spa             es
# 4. 葡萄牙语           por             pt
# 5. 瑞士语             swe             sv
# 6. 德语               deu             de
# 7. 阿拉伯语           arb             ar
# 8. 俄语               rus             ru
# 9. 法语               fra             fr
# 10.日语               jpn             ja