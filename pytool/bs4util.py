from bs4 import BeautifulSoup
import requests
import datetime
import json

headers= {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'zh-CN,zh;q=0.9',
'cache-control': 'max-age=0',
'cookie': 'B=17s48ohf7343b&b=3&s=vi; A3=d=AQABBGuQcV4CENeFySADe2JywU_yiMSI8BMFEgEBAQHhcl57XgAAAAAA_SMAAAcIa5BxXsSI8BM&S=AQAAAhmGLOk-qd7Dcz8wMHYyjHU; APID=UPc0d0c016-68ca-11ea-a723-06c362194baa; A1=d=AQABBGuQcV4CENeFySADe2JywU_yiMSI8BMFEgEBAQHhcl57XgAAAAAA_SMAAAcIa5BxXsSI8BM&S=AQAAAhmGLOk-qd7Dcz8wMHYyjHU; ucs=lbit=1584951070; A1S=d=AQABBGuQcV4CENeFySADe2JywU_yiMSI8BMFEgEBAQHhcl57XgAAAAAA_SMAAAcIa5BxXsSI8BM&S=AQAAAhmGLOk-qd7Dcz8wMHYyjHU&j=WORLD; APIDTS=1585193822; cmp=t=1585193915&j=0; GUCS=ARBij1S1; GUC=AQEBAQFecuFee0IaBgO4',
'sec-fetch-dest': 'document',
'sec-fetch-mode': 'navigate',
'sec-fetch-site': 'none',
'sec-fetch-user': '?1',
'upgrade-insecure-requests': '1'}

def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S ')

def getArticleUrl_YahooNews():
    yahoo='https://news.yahoo.com'
    global headers
    #print(headers)
    res=requests.get(yahoo,headers=headers)
    res.encoding="UTF-8"
    soup = BeautifulSoup(res.text,"html.parser")
    newsList=[]
    divs=soup.body.select("main")[0].contents
    wrap=divs[1].div.div.contents
    top=wrap[0]
    bottom=wrap[1]
    topHref=top.find('a')['href']
    newsList.append('legend-'+yahoo+topHref)
    lis=bottom.ul.contents
    for li in lis:
        newsList.append(yahoo+li.find('a')['href'])
    return newsList

def getArticleUrl_YahooHome():
    yahoo='http://www.yahoo.com'
    global headers
    res=requests.get(yahoo,headers=headers)
    res.encoding="UTF-8"
    soup = BeautifulSoup(res.text,"html.parser")
    #print(soup.prettify())
    newsList=[]
    divs=soup.select("main > div")
    div=divs[4]
    wrap=div.div.div.contents
    top=wrap[0]
    bottom=wrap[1]
    #print(top.prettify())
    topHref=top.div.div.a['href']
    newsList.append(yahoo+topHref)
    lis=bottom.ul.contents
    for li in lis:
        newsList.append(yahoo+li.a['href'])
    return newsList

def getArticle_YahooNews(url):
    global headers
   
    if 'legend-' in url:
        url=url.split('-')[1]
        print(url)
        return {'p-1':'暂不支持legend文章格式'}
    else:
        print(url)
        a={}
        res = requests.get(url,headers=headers)
        res.encoding="UTF-8"
        soup=BeautifulSoup(res.text,'html.parser')
        article=soup.body.find('article')
        source={}
        try:
            source['name']=article.find('a').string
            source['href']=article.find('a')['href']
            source['logo']=article.find('img')['src']
            a['source']=source
        except:
            print('解析source失败')
        try:    
            a['title']=article.header.header.h1.string
        except:
            print('解析title失败')
        try:    
            wrap=article.select('.caas-content-wrapper')[0]    
            author=wrap.contents[0].contents[0].div.div.string
            publishtime=wrap.contents[0].contents[0].div.time.string
            a['author']=author
            a['publishtime']=publishtime
        except:
            print('解析作者和发布时间失败')
        try:    
            contentWrap=article.select('.caas-content-wrapper')[0].contents[1]
            content={}
            recognizeContent(contentWrap,content,1)
            a['content']=content
        except:
            print("解析正文失败")
        return a

def getArticle_YahooHome_Lifestyle(url):
    global headers
    print(url)
    articleObj={}
    #url='https://news.yahoo.com/coronavirus-2-trillion-stimulus-deal-for-businesses-080739448.html'
    #使用request去get目标网址
    res = requests.get(url,headers=headers)
    #更改网页编码--------不改会乱码
    res.encoding="UTF-8"
    #创建一个BeautifulSoup对象
    soup=BeautifulSoup(res.text,'html.parser')

    header=soup.body.select('#YDC-Side-StackCompositeSideTop')[0]
    articleObj['title']=header.contents[0].find('h1').string
    articleObj['author']=header.contents[1].div.div.div.contents[1].contents[0].a.string
    articleObj['organization']=header.contents[1].div.div.div.contents[1].contents[1].span.find('a').string
    articleObj['publishtime']=header.contents[1].div.div.div.contents[1].contents[1].time.string
    articleObj['video']=''
    article=soup.body.find('article')
    contentWrap=article.contents[1]
    content={}
    recognizeContent(contentWrap,content,1)
    #for key in content.keys():
    #    print(key,content[key])
    articleObj['content']=content
    return articleObj
  
def recognizeContent(contentWrap,content,startNo):
    i=startNo
    for c in contentWrap.contents:
        no='_'+str(i)
        if c.name=='p':
            content['p'+no]=c.string
        elif c.name=='h1':
            content['h1'+no]=c.string
        elif c.name=='h2':
            content['h2'+no]=c.string
        elif c.name=='h3':
            content['h3'+no]=c.string            
        elif c.name=='blockquote':
            content['b'+no]=c.find('span').string
        elif c.name=='figure':
            img=c.find('img')
            src=img['src']
            data_src=img['data-src']
            if len(src)>0:
                r=src
            else:
                r=data_src  
            content['img'+no]=r     
        elif c.name=='div':
            recognizeContent(c,content,i)
        i=i+1
    
def printDict(d):
    for key in d.keys():
        print(key+":")
        if type(d[key]) is dict:
            print('--------------')
            printDict(d[key]) 
        else:
            print(d[key])
        print

def saveArticle():
    print('saveArticle')

def translateArticle(enA,cnA):
    for key in enA:
        enValue=enA[key]
        if  enValue is not None:
            if type(enValue) is dict:
                cnA[key]={}
                translateArticle(enA[key],cnA[key])
            else:
                if ('img' not in key)  and  ('src' not in key) and ('href' not in key):
                    cnString=translateString(enValue) 
                    cnA[key]=cnString
                else:
                    cnA[key]=enValue    

def resolveYoudao(result):
    j=json.loads(result)
    #print(j['errorCode'])
    if j['errorCode']==0:
        result = j['translateResult'][0][0]['tgt']
    else:
        result = 'translate error'
    #print (result)
    return result

def translateString(string):
    googleEngine='http://translate.google.cn/translate_a/single?client=gtx&dt=t&dj=1&ie=UTF-8&sl=auto&tl=zh&q='
    bingEngine='http://api.microsofttranslator.com/v2/Http.svc/Translate?appId=AFC76A66CF4F434ED080D245C30CF1E71C22959C&from=&to=en&text='
    youdaoEngine='http://fanyi.youdao.com/translate?&doctype=json&type=AUTO&i='
    engine=youdaoEngine
    url=engine+string
    headers={'user-agent': 'Mozilla/5.0'}
    res=requests.get(url,headers=headers)
    res.encoding="UTF-8"
    if engine == youdaoEngine:
        result=resolveYoudao(res.text)
    return result

def parseScript(url):
    global headers
    print(url)
    res = requests.get(url,headers=headers)
    res.encoding="UTF-8"
    soup=BeautifulSoup(res.text,'html.parser')
    article=soup.body.find('article')
    source={}

def main():
    print(now()+'start')
    
    url='legend-https://news.yahoo.com/tom-hanks-rita-wilson-joyful-231531631.html'
    r=parseScript(url)
    print(r)
    #cnArticle={}
    #translateArticle(article,cnArticle)
    #printDict(cnArticle)
   # print(str(cnArticle))
    #msg='The unanimous vote came despite misgivings on both sides about whether it goes too far or not far enough and capped days of difficult negotiations as Washington confronted a national challenge unlike it has ever faced.'
    #translateString(msg)

    print('end')

if __name__== '__main__':
    main()    