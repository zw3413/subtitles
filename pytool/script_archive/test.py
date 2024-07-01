import os
import sys
import streamlink
import re
import hashlib
from bs4 import BeautifulSoup
import requests
from faster_whisper import WhisperModel
import torch
from datetime import timedelta, datetime
from selenium import webdriver
import utils
import request
import time
from utils import Unbuffered

#from seamless_communication.inference import Translator

filePath_prefix = '../file/subtitle/'
MP3_afterfix = '.mp3'
SRT_afterfix = '.srt'
FLV_afterfix = '.flv'

current_directory = os.path.dirname(os.path.abspath(__file__))

print(current_directory)

te = open(current_directory+"/../file/log/subtitle.log",'a', encoding='utf-8')  # File where you need to keep the logs



sys.stdout=Unbuffered(sys.stdout)
#命令行的方式播放视频
def play (url, quality = 'best'):
    cmd = 'streamlink --http-header "User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 AOL/9.8 AOLBuild/4346.2019.US Safari/537.36" --http-header "Referer=" "hlsvariant://'+ url +'" '+quality
    print(cmd)
    output = os.system(cmd)
    print(output)

#python库的方式下载视频
def download(url, quality = 'best'):
    streams = streamlink.streams(url)
    fd = streams[quality].open()
    fd.save()
    #data = fd.read(1024)
    fd.close()
    #print(data)
    return

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
        cmd = 'streamlink --retry-max 10 --stream-segment-timeout 30 --stream-segment-threads '+threads+' -o "'+filePath+'" --http-header "User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 AOL/9.8 AOLBuild/4346.2019.US Safari/537.36"  '+ url +' '+quality
    else:
        cmd = 'streamlink --retry-max 10 --stream-segment-timeout 30 --stream-segment-threads '+threads+' -o "'+filePath+'" --http-header "User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 AOL/9.8 AOLBuild/4346.2019.US Safari/537.36" --http-header "Referer=" "hlsvariant://'+ url +'" '+quality
    
    print(cmd)
    
    
    output = os.system(cmd)
    return output,fileName    

def convertFlvToMp3(flvPath):
    mp3Path = flvPath.replace(FLV_afterfix, MP3_afterfix).replace('_worst','').replace('_best','')
    cmd = 'ffmpeg -i '+flvPath+' -c:v none -c:a libmp3lame -b:a 320k -joint_stereo 0 -y -format mp3 -metadata artist="missav" -metadata title="" -metadata album="x" '+mp3Path
    #print(cmd)
    output = os.system(cmd)
    #print(output)
    return mp3Path,output


#命令行的方式使用streamlink下载视频，pipe到ffmpeg转换为mp3格式
def downloadAudio(url):

    fileName =  str(hashlib.md5(url.encode()))  #默认取资源地址的md5作为文件名
   
    match = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", url)
    if match != None:
        fileName = match.group(0)

    filePath = filePath_prefix + fileName + MP3_afterfix
    cmd = 'streamlink -O --hls-segment-threads 5 --http-header "User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 AOL/9.8 AOLBuild/4346.2019.US Safari/537.36" --http-header "Referer=" "hlsvariant://'+  url +'" worst | ffmpeg -i pipe:0 -c:v none -c:a libmp3lame -b:a 320k -joint_stereo 0 -y -format mp3 -metadata artist="missav" -metadata title="'+fileName+'" -metadata album="x" '+filePath
    #print(cmd)
    output = os.system(cmd)
    #print(output)
    return fileName+MP3_afterfix,output

#使用Faster-Whisper从音频或者视频获取到字幕
# def transcribeWithFW(filePath, ms = 'large-v3'): #base
def transcribeWithFW(filePath, ms = 'base'): #
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if torch.cuda.is_available() else "int8"
        model_size = ms
        model = WhisperModel(model_size, device = device , compute_type= compute_type)
        segments, info = model.transcribe(filePath, beam_size=5, vad_filter=True, task = "transcribe")
        language = info.language
        print("Detected language '%s' with probability %f" % (language, info.language_probability))
        #srtPath = filePath.split('.')[0]+ info.language + '.srt'
        srtPath = filePath.replace(MP3_afterfix,SRT_afterfix).replace(FLV_afterfix, SRT_afterfix).replace('_worst','').replace('_best','')
            #delete the file at filePath if exist
        if os.path.exists(srtPath):
            os.remove(srtPath)
        f = open(srtPath,"w", encoding='utf-8')
        print(srtPath)
        lineCount = 1
        t_start = datetime.now()
        for segment in segments :
            f.write(str(lineCount)+"\n")
            s = utils.secondsToStr(segment.start)
            e = utils.secondsToStr(segment.end)
            f.write( s + ' --> ' + e +"\n")
            f.write(segment.text+"\n")
            f.write("\n")
            print(str(timedelta(seconds=(datetime.now() - t_start).total_seconds())) + " ["+s+"s -> "+e+"s] %s" % (segment.text))
            lineCount = lineCount + 1
            f.flush()
        f.close()
        print("subtitleXLog:字幕写入完成")
        #return language, srtPath
    except Exception as e:
        print("subtitleXLog:字幕生成失败")
        print(e)
        return "error", "error"

#从一个missav视频链接，获取到其视频m3u8链接地址
#参考https://www.jianshu.com/p/7b760e2db555
def resolvMissav(url):
    global headers
    driver = webdriver.Chrome()
    driver.implicitly_wait(2)
    driver.get(url)
    m3u8Url = driver.execute_script("return window.source1280")
    driver.quit()
    return m3u8Url

#whisper 9b00428e-f6c7-46e6-ba92-516123b89efb.mp3 --language Japanese --task translate
def main(argv):
    #convertFlvToMp3(filePath_prefix +"d131749d-18e2-42fe-ad5e-382131f5cf4b.flv")
    #downloadCmd("https://static.serioushammerz.com/d131749d-18e2-42fe-ad5e-382131f5cf4b/1280x720/video.m3u8")
    cmd = argv[1]
    #cmd = "download"
    seed = {}
    if cmd == "download":
        try:
            #print(cmd,"获取待下载的seed")
            seeds = request.GetNextNeedProcessSeed("download")
            # if the json array seeds length is zero, then stop the precess
            if seeds is None or len(seeds) == 0 :
                #print(cmd,"没有待下载的seed")
                return 0
            seed = seeds[0]  
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
  
    if cmd == "transcribe":  
        try:
            #print(cmd,"获取待转文字的seed")
            seeds = request.GetNextNeedProcessSeed("transcribe")
            if seeds is None or len(seeds) == 0 :
                #print(cmd,"没有待转文字的seed")
                return 0
            seed = seeds[0]  
            id = seed["id"]
            print(cmd,"开始转换文字seed："+str(id))
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
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(device)
            compute_type = "float16" if torch.cuda.is_available() else "int8"
            model_size = 'large-v3' # "base" # 
            model = WhisperModel(model_size, device = device , compute_type= compute_type, local_files_only = False)
            segments, info = model.transcribe(filePath_prefix+flvPath, beam_size=5, vad_filter=True, task = "transcribe")
            language = info.language
            print(cmd,"Detected language '%s' with probability %f" % (language, info.language_probability))
            #srtPath = filePath.split('.')[0]+ info.language + '.srt'
            srtPath = filePath_prefix + flvPath.replace(MP3_afterfix,SRT_afterfix).replace(FLV_afterfix, SRT_afterfix).replace('_worst','').replace('_best','')
                #delete the file at filePath if exist
            if os.path.exists(srtPath):
                os.remove(srtPath)
            f = open(srtPath, "w", encoding='utf-8')
            print(cmd,srtPath)
            lineCount = 1
            t_start = datetime.now()
            for segment in segments :
                #print("write linecount")
                f.write(str(lineCount)+"\n")
                print(str(lineCount))
                s = utils.secondsToStr(segment.start)
                e = utils.secondsToStr(segment.end)
                f.write( s + ' --> ' + e +"\n")
                print(s + ' --> ' + e)
                #print("write segment text")
                #str_content = str(segment.text.encode('gbk'),encoding = 'utf-8')
                f.write(segment.text)
                f.write("\n")
                print(segment.text)
                lineCount = lineCount + 1
                f.flush()
                #print("flush")
            #print("over")
            #print("closed")
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
            print(cmd,"字幕写入完成")
        except Exception as e:
            print(cmd,"字幕生成失败")
            print(e)
            seed["process_status"] = "2e"
            seed["err_msg"] = cmd + "字幕生成失败" + str(e)
            request.SaveSeed(seed)
           
            
    if cmd =="downloadbesttofile":
        url = argv[2]
        downloadFlv(url, 'best')
    
    # if cmd =="translate":
    #     # 3 表示完成 x->eng 的翻译，或者初始视频就是eng
    #     model_name = "seamlessM4T_medium"
    #     vocoder_name = "vocoder_v2" #if model_name == "seamlessM4T_v2_large" else "vocoder_36langs"
    #     translator = Translator(
    #         model_name,
    #         vocoder_name,
    #         device=torch.device("cuda:0"),
    #         dtype=torch.float16,
    #     )
    #     #tgt_langs = ("arb", "rus", "ind", "tam", "kor","cmn")

    #     file_path = "../file/subtitle/abc/jpn1.srt"
    #     file = open(file_path, "r")
    #     #content = file.read()
    #     #print(len(content))


    #     #for tgt_lang in tgt_langs:

    #         # text_output, speech_output = translator.predict(
    #         #     input="Hey everyone! I hope you're all doing well. Thank you for attending our workshop.",
    #         #     task_str="t2tt",
    #         #     tgt_lang=tgt_lang,
    #         #     src_lang="eng",
    #         # )
            
    #     try:
    #         for l in file:
    #             line = l.strip()
    #             print(line)
    #             pattern_num = r'^-?\d+$'
    #             pattern_timestamp = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$')
    #             if re.match(pattern_num, line) or re.match(pattern_timestamp, line):
    #                 print(line)
    #             else:        
    #                 tgt_lang ="eng"
    #                 text_output_en, speech_output = translator.predict(
    #                     #input="Hey everyone! I hope you're all doing well. Thank you for attending our workshop.",
    #                     input = line,
    #                     task_str="t2tt",
    #                     tgt_lang=tgt_lang,
    #                     src_lang="jpn",
    #                 )
    #                 print(f"Translated text in {tgt_lang}: {text_output_en[0]}")
                
    #     finally:
    #         file.close()
    
    
    #     return 0
    
    
    
    try:
        te.close()
    except: 
        pass
               

         
        
    # cmd = argv[1]
    # #命令参数1
    # #网页的m3u8链接地址
    # param1 = argv[2]
    # if cmd == 'ProduceSubtitle':
    #     m3u8Url = param1
    #     originalLanguage, srtPath = ProduceSubtitle(m3u8Url)
    #     print(originalLanguage, srtPath)


    #url = 'https://missav.com/maan-748'
    #m3u8Url = resolvMissav(url)
    #print(m3u8Url)
    
    #filename = "afee3ad4-641a-41af-bce2-ea09d4fd11f2_best.flv"
    #transcribeWithFW(filename)

    # url1 = 'https://avdocker.com/47267a14-426f-497e-a720-53156ff5e287/playlist.m3u8'
    # url2 = 'https://avdocker.com/bf74fd6f-3a37-4052-b970-6b3c6c466504/playlist.m3u8'
    # url3 = 'https://avdocker.com/9b00428e-f6c7-46e6-ba92-516123b89efb/playlist.m3u8'
    # url4 = 'https://kx35.geekwaver.com/54b94b4b-b403-4f7a-8d37-ddb59a6cb666/playlist.m3u8'
    #url5 = 'https://static.eggsummibut.com/f3669db7-7ae3-4c60-b18f-5d745fbe9231/1280x720/video.m3u8'
    #downloadAudio("https://static.itjustqwerty.com/c7e0b5a7-03b5-4388-aed2-eccf1261b67d/1280x720/video.m3u8")

    # urls = [
    #     'https://kx35.geekwaver.com/54b94b4b-b403-4f7a-8d37-ddb59a6cb666/playlist.m3u8',
    #     'https://avdocker.com/1377cd40-ab2c-47d4-8010-a48e75d622cb/playlist.m3u8',
    #     'https://avdocker.com/d63b978c-3cda-4ee9-b68e-d152b66cc49a/playlist.m3u8'
    # ]
    #play(url)
    #for url in urls :
    #    downloadCmd(url)

    #pageUrl1 = 'https://missav.com/cn/sone-010'
    #m3u8Url1 = resolvMissav(pageUrl1)
    #print(m3u8Url1)
    #downloadCmd(m3u8Url1)


headers= {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'cookie': '',
            'Referer':'https://missav.com',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1'}

if __name__ == "__main__" :
    main(sys.argv[0:])