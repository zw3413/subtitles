import requests
import json

#serverIp = "http://127.0.0.1:12801"
#serverIp = "https://api.subtitlex.xyz"
serverIp = "http://192.168.2.202:12801"


def GetNextNeedProcessSeed(type):
    try:
        url = serverIp+"/seed_need_process?type="+type
        r = requests.post(url,timeout=60)
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

def GetSubtitleInfo(id,lang):
    try:
        url = serverIp+"/get_subtitle_info?id="+str(id)+"&lang="+lang
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

def PostWantFullfilled(want_id, errorMsg):
    try:
        url = serverIp + "/update_want_fullfilled"
        r =  requests.post(url+"?want_id="+str(want_id)+"&fullfilled="+errorMsg ,timeout=60)
        jData = json.loads(r.text)
        return jData
    except Exception as e:
        print(e)
        return []


def main():
    GetNextNeedProcessSeed()  

if __name__ == "__main__" :
    main()