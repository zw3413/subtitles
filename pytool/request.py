import requests
import json
import os
from utils import *

#serverIp = "http://127.0.0.1:12801"
#serverIp = "https://api.subtitlex.xyz"
serverIp = "http://192.168.2.101:12801"

def remote_call(f, pl):  
    headers = {  
        "Content-Type": "application/json",  
    }  
    data = {  
        "hashcode": "xxx",  
        "request_id": "xxx",  
        "device_ip": "0.0.0.0",  
        "function": f,  
        "params": pl,  
    }  
    try:  
        response = requests.post(serverIp + "/common/allPurpose", headers=headers, data=json.dumps(data))  
        if response.status_code == 200:  
            return response.json()  
        else:  
            # TODO: 显示调用失败的消息给用户  
            print(f"Call failed with status code: {response.status_code}")  
            return None  
    except requests.RequestException as e:  
        # TODO: 显示调用失败的消息给用户  
        print(f"Call failed: {e}")  
        return None

def getSeedNeedProcess(type):
    pl = [type]
    print("remote_call p_get_need_process")
    result = remote_call("p_get_need_process", pl)
    print(result)
    if result["rc"] == "000":
        return json.loads(result["data"])
    else:
        return None

def UpdateSeedStatus(seed_id, status):
    pl = [seed_id, status]
    return remote_call("p_update_seed_status", pl)

def UpdateSubtitleLang(subtitle_id, lang):
    pl = [subtitle_id, lang]
    return remote_call("p_update_subtitle_lang", pl)

def upload_file(file_path, url):
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            print("File uploaded successfully!")
        else:
            print("Failed to upload file. Status code:", response.status_code)
            print("Response:", response.text)


def PushSubtitleToServer(tgt_path, file_name):
    upload_url = serverIp+"/upload-files?filename="+file_name 
    file_path = tgt_path
    upload_file(file_path, upload_url)


def PullSrtFromServer(seed, LocalPathPrefix, subtitleId = ''):
    try:
        id = str(seed["id"])
        video_language = seed["video_language"]
        srt_path = seed["srt_path"]
        if video_language is not None and len(video_language)>0:
            src_lang = language_codes[video_language]
            url = serverIp + "/get_subtitle?id="+id+"&language="+src_lang+"&titleSubaId="+ subtitleId
        elif srt_path is not None:
            url = serverIp + "/get_subtitle?srt_path="+srt_path
        else:
            raise Exception("No srt file path provided")

        tgt_path = LocalPathPrefix+srt_path
        if not os.path.exists(tgt_path):
            r= requests.get(url)
            tgt_file = open(tgt_path, "w", encoding='utf-8')
            tgt_file.write(r.text)
            tgt_file.flush()
        
    except Exception as e:
        print(e)

def PullSrtFromServerBySubtitleId(subtitleId,src_path, LocalPathPrefix):
    url = serverIp + "/get_subtitle?titleSubaId="+ subtitleId
    r= requests.get(url)
    tgt_path = LocalPathPrefix + src_path
    parent_path = os.path.dirname(tgt_path)
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)
    if os.path.exists(tgt_path):
        os.remove(tgt_path)
    tgt_file = open(tgt_path, "w", encoding='utf-8')
    tgt_file.write(r.text)   
    return tgt_path 

def GetNextNeedProcessSeed(type):
    try:
        url = serverIp+"/seed_need_process?type="+type
        r = requests.post(url,timeout=60)
        jData = json.loads(r.text)
        return jData
    except Exception as e:
        print(e)
        return []

def GetSeed(hint):
    try:
        url = serverIp+"/get_seed?hint="+hint
        r = requests.post(url, timeout=60)
        jData = json.loads(r.text)
        return jData
    except Exception as e:
        print(e)
        return []

def SaveSeed(seed):
    try:
        url = serverIp+"/save_seed"
        #print("SaveSeed:")
        #print(seed)
        r = requests.post(url, json=seed,timeout=60)
        jData = json.loads(r.text)
        return jData
    except Exception as e:
        print(e)
        return 

def SaveSubtitle(subtitle):
    try:
        url = serverIp+"/save_subtitle"
        #print("SaveSubtitle:")
        #print(subtitle)
        r = requests.post(url, json=subtitle,timeout=60)
        jData = json.loads(r.text)
        return jData
    except Exception as e:
        print(e)
        return 

def GetSubtitleInfo(id,lang='',subtitleId= ''):
    try:
        url = serverIp+"/get_subtitle_info?id="+str(id)+"&lang="+lang+"&titleSubaId="+ subtitleId
        #print("GetSubtitle:"+str(id)+", Lang:"+lang)
        r = requests.post(url, timeout=60)
        jData =json.loads(r.text)
        return jData
    except Exception as e:
        print(e)
        return []

def GetWantsNotProcessed(id):
    try:
        url =  serverIp +"/get_wants_not_process?seed_id="+id
        r = requests.post(url, timeout=60)
        jData = json.loads(r.text)
        return jData
    except Exception as e:
        print(e)
        return []

def GetWantSeed():
    try:
        url = serverIp + "/get_want_seed"
        r = requests.post(url, timeout= 60)
        jData = json.loads(r.text)
        return jData
    except Exception as e:
        print(e)
        return []

def GetPendingTranslateSeed():
    try:
        pl = []
        print("remote_call p_get_pending_translate_seed")
        result = remote_call("p_get_pending_translate_seed", pl)
        print(result)
        if result["rc"] == "000":
            return json.loads(result["data"])
        else:
            return None
    except Exception as e:
        print(e)
        return None

def PostWantFullfilled(want_id, errorMsg):
    try:
        url = serverIp + "/update_want_fullfilled"
        r =  requests.post(url+"?want_id="+str(want_id)+"&fullfilled="+errorMsg ,timeout=60)
        jData = json.loads(r.text)
        return jData
    except Exception as e:
        print(e)
        return []


# def main():
#     GetNextNeedProcessSeed()  

# if __name__ == "__main__" :
#     main()