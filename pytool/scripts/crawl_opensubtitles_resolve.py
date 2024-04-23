import os  
import requests  
from urllib.parse import urlparse  
import cgi
import zipfile
import re
import glob
import redis
r = redis.Redis(host='192.168.2.203', port=6379, db=0,decode_responses=True)  



cwd = os.getcwd()
print(cwd)
import sys
sys.path.append(cwd)
import request


FILE_PATH_PREFIX = cwd+'\\scripts\\file\\opensubtitles\\'
#FILE_PATH_PREFIX = r'\\192.168.2.201\\d\\opensubs\\'
#FILE_PATH_PREFIX = r'd:/opensubs/'


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/?type=https").json()

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

def increment_counter():  
    # 使用INCR命令递增my_counter的值  
    new_value = r.incr('opensubs_crawl_counter')  
    # 如果需要的话，你可以使用GET命令来获取当前值  
    # current_value = r.get('my_counter')  
    # 注意：get命令返回的是字节串，如果需要整数，需要进行转换：current_value = int(current_value)  
    return new_value


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
download_dir = FILE_PATH_PREFIX
chrome_options.add_experimental_option('prefs', {
    "download.default_directory": download_dir,
    #"download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    'window-size':'300,300'
})
chrome_options.add_argument('blink-settings=imagesEnabled=false')
chrome_options.add_argument('window-size=300,300')
import time
proxy_count =5
useProxy = False
def download_file_with_selenium(url):
    global id, proxy, proxy_count
    if useProxy:
        if proxy is None:
            proxy = get_proxy().get("proxy")
            print(f"Using proxy {proxy}")
        proxy_count -= 1
        if proxy_count < 0:
            delete_proxy(proxy)
            proxy = get_proxy().get("proxy")
            print(f"Using proxy {proxy}")
            proxy_count = 20
    chrome_options.add_argument("--proxy-server=%s" % proxy) 
    driver = webdriver.Chrome(options=chrome_options)
    try:
        #url = 'https://www.baidu.com'
        driver.get(url)
        wait_time = 10
        while wait_time > 0 :
            time.sleep(2)
            for root, dirs, files in os.walk(FILE_PATH_PREFIX):  
                # 对于每个文件，检查其后缀是否为所需的后缀  
                for file in files:  
                    if file.endswith('.zip'):
                        file_path = os.path.join(root, file)  
                        return file_path, file 
            wait_time -= 1
        return None, None
    except Exception as e:
        print(e)
    finally:
        driver.quit() 
        
proxy = None
def download_file_from_url(url):  
    global proxy_count, proxy
    proxy_count -= 1
    local_path = None
    local_filename = None
    if proxy is None:
        proxy = get_proxy().get("proxy")
    if proxy_count < 0 :
        delete_proxy(proxy)
        proxy = get_proxy().get("proxy")
    print(f"Using proxy {proxy}")
    retry_count = 1
    while retry_count <= 3 :
        try:  
            print(f"retry {retry_count}")
            retry_count += 1
            proxy = {"http": "http://{}".format(proxy),"http": "http://{}".format(proxy)},
            #response = requests.get(url,allow_redirects=True ,stream=True,proxies={"http": "http://{}".format(proxy),"https": "http://{}".format(proxy)}, timeout=30)  
            response = requests.get(url,allow_redirects=True ,stream=True,proxies= timeout=30)  

            if response.status_code == 404:
                return '404', None
            response.raise_for_status()  # 再次检查GET请求的状态  
            filename = None  
            content_disposition = response.headers.get('Content-Disposition')  
            if content_disposition:  
                _, params = cgi.parse_header(content_disposition)  
                filename = params.get('filename')    
            if not filename:  
                # 如果Content-Disposition中没有文件名，则使用URL的最后一部分作为文件名  
                filename = os.path.basename(urlparse(url).path)  
        
            # 构造完整的本地文件路径  
            local_filename = filename  
            local_path = os.path.join(FILE_PATH_PREFIX, local_filename)    
            with open(local_path, 'wb') as f:  
                for chunk in response.iter_content(chunk_size=8192):  
                    if chunk:  # 过滤掉空的chunks  
                        f.write(chunk) 
            return local_path,  local_filename
        except Exception as e:
            if local_path and os.path.exists(local_path):
                os.remove(local_path)  # 如果文件已经部分写入，删除它
            print(f"Failed to download file from {url}. Error: {e}")
            delete_proxy(proxy)
            proxy = get_proxy().get("proxy")
            print(f"Using proxy {proxy}")
    return None, None
    #print(f"File {filename} downloaded successfully.")  
    

def unzip_file(zip_filepath, dest_path):  
    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:  
        zip_ref.extractall(dest_path)  

def find_files_with_suffix(suffix, path='.'):  
    """  
    在给定路径下查找具有特定后缀的文件。  
  
    参数:  
    suffix (str): 要查找的文件后缀。  
    path (str): 要开始搜索的目录路径。默认为当前目录。  
  
    返回:  
    list: 包含找到的文件路径的列表。  
    """  
    # 初始化一个空列表来存储找到的文件路径  
    file_paths = []  
  
    # 遍历给定路径下的所有文件和子文件夹  
    for root, dirs, files in os.walk(path):  
        # 对于每个文件，检查其后缀是否为所需的后缀  
        for file in files:  
            if file.endswith(suffix):  
                # 如果是，则将其完整路径添加到列表中  
                file_paths.append(os.path.join(root, file))  
  
    return file_paths  

def find_files_without_suffix(suffix, path='.'):  
    # 初始化一个空列表来存储找到的文件路径  
    file_paths = []  
    # 遍历给定路径下的所有文件和子文件夹  
    for root, dirs, files in os.walk(path):  
        # 对于每个文件，检查其后缀是否为所需的后缀  
        for file in files:  
            if not file.endswith(suffix):  
                # 如果是，则将其完整路径添加到列表中  
                file_paths.append(file)  
    return file_paths  

def parse_nfo_file(nfo_path):  
    line_count = 0 
    pattern_name = re.compile(r'^Û\s+(.*\s+subtitles)\s+Û$')
    line_count_name = 10000
    pattern_movie_info_start = re.compile(r'^Û\s+MOVIE INFORMATION\s+Û$') 
    line_count_movie_info_start = 10000
    pattern_subtitle_info_start = re.compile(r'^Û\s+SUBTITLE INFORMATION\s+Û$') 
    line_count_subtitle_info_start = 10000
    pattern_cd_info_start = re.compile(r'^Û\s+[0-9]+\.CD INFORMATION\s+Û$') 
    current_cd_count = 0
    line_count_current_cd = 10000
    keywords = ['Link', 'Filename', 'Language', 'Format', 'Total', 'Release Name']  
    movie_info = {'Name':'','Link':'', 'Language':'', 'Filename':'', 'Format':'', 'Total':'', 'Release Name':''}  

    with open(nfo_path, 'r', encoding='utf-8') as nfo_file:  
        for line in nfo_file:
            line_count = line_count + 1

            if line_count < line_count_name:
                match = pattern_name.search(line)
                if match:
                    movie_info['Name'] = match.group(1).strip()
                    line_count_name = line_count

            if re.match(pattern_subtitle_info_start, line):#获取subtitle info开始行数
                line_count_subtitle_info_start = line_count 
                #print("found line_count_subtitle_info_start",line_count_subtitle_info_start)

            if re.match(pattern_cd_info_start, line):#获取cd info开始行数
                line_count_current_cd = line_count
                #print("found line_count_current_cd",line_count_current_cd)

            if line_count >= line_count_subtitle_info_start + 2 and line_count <  line_count_current_cd :#解析subtitle info
                for keyword in keywords:  
                    pattern = re.compile(f'^Û\\s+{re.escape(keyword)}\\s+:\\s+(.*)\\s+Û$', re.IGNORECASE)  
                    match = pattern.search(line)  
                    if match:  
                        movie_info[keyword] = match.group(1).strip()  
    return movie_info  

id = 0
while True:
    id = increment_counter()
    print("dealing "+str(id))
    if id > 10000000 :
        break
    if r.sismember('opensubs_crawl_dealed', id):
        continue
    try:
        #https://www.opensubtitles.org/en/subtitleserve/sub/9718896
        #url_base = r"https://www.opensubtitles.org/en/subtitleserve/sub/"
        url_base = r"https://dl.opensubtitles.org/en/download/sub/"

        url = url_base + str(id)

        #下载
        retry_count = 5
        local_path = None
        local_filename = None
        while retry_count >0 :
            local_path, local_filename = download_file_from_url(url)
            #local_path, local_filename = download_file_with_selenium(url)
            if local_path is not None:
                break   
            retry_count -= 1

        if local_path == '404':
            r.sadd('opensubs_crawl_dealed', id)
            print("id "+str(id) + "失败  404")
            continue
        
        if local_path is None:
            raise Exception("id"+str(id)+"下载失败")
        #local_path = FILE_PATH_PREFIX+"alien3.(1992).eng.2cd.(1).zip"

        #解压缩

        zip_file = local_path  # 替换为你的zip文件路径  
        dest_folder = FILE_PATH_PREFIX+"unzip\\"+str(id)+"\\"  # 替换为你想解压到的目标文件夹路径  
        unzip_file(zip_file, dest_folder)

        #找到nfo文件
        sub_files = find_files_with_suffix('nfo',dest_folder)
        sub_file = sub_files[0]

        #读取nfo
        movie_info = parse_nfo_file(sub_file)

        #获取字幕路径
        subtitle = find_files_without_suffix('nfo', dest_folder)
        subtitles = '&&&&'.join(subtitle)

        #存库
        params = [str(id), movie_info['Name'] ,movie_info['Link'],  movie_info['Language'], movie_info['Filename'], movie_info['Format'], movie_info['Total'], movie_info['Release Name'], subtitles]
        result = request.remote_call('p_save_opensubtitles',params)
        if result['rc'] != '000':
            print(result['rc'], result['rm'])
            continue
        r.sadd('opensubs_crawl_dealed', id)

    except Exception as e:
        print("id "+str(id) + "失败")
        print(e)

    
