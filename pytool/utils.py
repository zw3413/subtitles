from functools import reduce
import re

filePath_prefix = '../file/subtitle/'
cmd = "translate"
pattern_num = r'^-?\d+$' #regx pattern of No. 
pattern_timestamp = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$') #regx pattern of timestamp
pattern_domain = r'^http[s]://(?:[a-zA-Z]|[0-9]|[$-.@+])+'


tgt_langs = ("cmn","cmn_Hant","spa","por","swe","deu","arb","rus","fra","jpn")

def secondsToStr(t):
    return "%02d:%02d:%02d,%03d" % reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],[(round(t*1000),),1000,60,60])

language_codes = {
    "en": "eng",
    "zh": "cmn",
    "yue":"cmn_Hant",
    "es": "spa",
    "pt": "por",
    "sv": "swe",
    "de":"deu",
    "ar":"arb",
    "ru":"rus",
    "fr":"fra",
    "ja":"jpn"
}


def langCode3To2(c3):

    for key, value in language_codes.items():
        if value == c3:
            return key
    return "notfound"

def langCode2To3(c2):
    return language_codes[c2]

def split_text(text, length):
    text_list=[]
    tmp = text[:int(length)]
    # print(tmp)
    # 将固定长度的字符串添加到列表中
    text_list.append(tmp)
    # 将原串替换
    text = text.replace(tmp, '')
    if len(text) < length + 1:
        # 直接添加或者舍弃
        text_list.append(text)
    else:
        split_text(text, length)
    return text_list

def now():
    import time
    return time.asctime(time.localtime(time.time()))
