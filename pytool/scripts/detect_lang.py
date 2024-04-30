import os, redis, re,sys
import langid
from iso639 import Lang
sys.path.append(os.getcwd())
import request, utils
import time

r = redis.Redis(host='192.168.2.203', port=6379, db=0,decode_responses=True)  
redis_key = 'zmb_pending_subtitle_id_1'
error_redis_key = 'zmb_pending_subtitle_id_1_error'
path_prefix = '\\\\192.168.2.201\\Developer\\Subtitles\\file\\subtitle\\'
def detect_lang():
    subtitle_id = r.rpop(redis_key)
    #subtitle_id = '46873'
    #subtitle_id = '49506'
    try:
        subtitle_array = request.GetSubtitleInfo('','',subtitle_id)  #获取源语言
        if subtitle_array is None or len(subtitle_array) == 0 :
            return
        path = subtitle_array[0]['path']
        file_path = path_prefix + path
        encoding = utils.detect_encoding(file_path=file_path)
        if encoding == 'GB2312':
            encoding = 'GBK'
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            count = 20
            detect_lang = None
            for line in f:
                line = line.strip()
                count -= 1
                if count < 0 :
                    break
                if len(line) > 0:
                    if (not re.match(utils.pattern_timestamp, line)) and (not re.match(utils.pattern_num, line)):
                        det = langid.classify(line)
                        lg = Lang(det[0])
                        if detect_lang is None:
                            detect_lang = lg.pt3
                        else :
                            if lg.pt3 == detect_lang:
                                continue
                            else:
                                r.lpush(error_redis_key, subtitle_id)
            if detect_lang != 'zho':
                print(subtitle_id, detect_lang)
                if utils.check_if_valid_lang_code3(detect_lang):
                    result = request.UpdateSubtitleLang(subtitle_id, detect_lang)                    
                    if result['rc'] != '000':
                        print(result)
                        r.lpush(error_redis_key, subtitle_id)
                else :
                    print("未知语言 ", end=' ')
                    print(subtitle_id, detect_lang)
    except Exception as e:
        print("报错", end=" ")
        print(e)
        r.lpush(redis_key, subtitle_id)



while True:
    detect_lang()