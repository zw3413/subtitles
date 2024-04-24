import requests, time
from bs4 import BeautifulSoup
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #'Accept-Encoding':'gzip, deflate, br, zstd',
    'Accept-Language':'en-CA,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    #'Pragma':'no-cache',
    'Priority':'u=0, i',
    'Content-Type': 'application/x-www-form-urlencoded'
}
video_nos = [
    # "embd-001",
    # "spz-418",
    # "xrw-828",
    "ipx-416",
    "gg-231",
    "venu-975",
    "ipx-149",
    "adn-014"
]


url_base = 'https://subscene.com/subtitles/{}'

for video_no in video_nos:
    video_no = video_no.replace('-uncensored-leak','')
    print(f"dealing {video_no}")
    urls =[ url_base.format(video_no),
        url_base.format('jav-'+video_no),
    ]
    for url in urls:
        print(f'requesting {url}', end=' ')
        response = requests.get(url=url, headers=headers)
        if response.status_code == 404:
            print("没有找到 404")
            continue
        if response.status_code == 409:
            print("被封锁 409 稍后重新请求")
            urls.append(url)
            continue
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tds = soup.find_all('td')
            for td in tds:
                if td.get('class').count('a1')>0:
                    print()
                    print("找到"+td.a.get('href'))
                    break  
        else :
            print("请求失败 "+ str(response.status_code))
            continue
        #time.sleep(2)       



