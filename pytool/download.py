import os
import re
import hashlib
import request
import time
from utils import *
import sys

class Unbuffered:
    def __init__(self, stream):
       self.stream = stream

    def write(self, data):
        try:        
            self.stream.write(data)
            self.stream.flush()
            te1.write(data)    # Write the data of stdout here to a text file as well
            te1.flush()
        except Exception as e:
            pass
    
    def flush(data):
        try:
            te1.flush()
        except Exception as e:
            pass

filePath_prefix = '../file/subtitle/'
video_filePath_prefix = 'D:\\abc\\'
MP3_afterfix = '.mp3'
SRT_afterfix = '.srt'
FLV_afterfix = '.flv'

current_directory = os.path.dirname(os.path.abspath(__file__))
te1 = open(current_directory+"/../file/log/subtitle_download.log",'a', encoding='utf-8')  # File where you need to keep the logs
sys.stdout=Unbuffered(sys.stdout)

#命令行的方式使用streamlink下载视频
def downloadFlv(url,  quality = 'worst', origin = ''):
    threads = '8'
    quality = quality # "worst"
    afterfix = FLV_afterfix
    fileName =  hashlib.md5(url.encode()).hexdigest() +afterfix
    match = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", url)
    if match != None:
        fileName = match.group(0)+afterfix
    filePath = video_filePath_prefix + fileName
    #delete the file at filePath if exist
    if os.path.exists(filePath):
        os.remove(filePath)
    if str.lower('youtube.com') in url:
        #cmd = 'streamlink --retry-max 200  --stream-segment-attempts 20 --stream-segment-timeout 60 --stream-timeout 720 --http-timeout 720 --stream-segment-threads '+threads+' -o "'+filePath+'" --http-header "User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 AOL/9.8 AOLBuild/4346.2019.US Safari/537.36"  '+ url +' '+quality
        
        cmd = 'yt-dlp -f worst --merge-output-format flv -o "'+filePath+'" https://www.youtube.com/watch?v=i2Z_nKRgDyU'
    else:
        cmd = 'streamlink --retry-max 3 --retry-streams 10 --stream-segment-attempts 20 --stream-segment-timeout 60 --stream-timeout 120 --http-timeout 120 --stream-segment-threads '+threads+' -o "'+filePath+'" --http-header "User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 AOL/9.8 AOLBuild/4346.2019.US Safari/537.36" --http-header "Origin='+ origin +'" "hlsvariant://'+ url +'" '+quality
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
        quality = 'worst'
        pageUrl = seed["video_page_url"]

        #使用bs重新获取video_m3u8_url


        match = re.findall(pattern_domain, pageUrl)
        if len(match)>0:
            origin = match[0]
        else:
            origin = ''
        #origin = 'https://missav.com'
        output, flvPath = downloadFlv(video_m3u8_url,quality,origin)
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


def download():
    while True:
        try:
            download_func()
        finally:
            time.sleep(5)
    
download()