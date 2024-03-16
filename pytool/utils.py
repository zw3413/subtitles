from functools import reduce

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

