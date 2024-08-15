import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import os
# import undetected_chromedriver as uc

print(os.getcwd())
import sys
#sys.path.append(r'C:\\Developer\\Subtitles\\pytool\\')
sys.path.append(os.getcwd())
import request

url_pattern = re.compile(r'^.+/dm\d+/en/.+$')

#from selenium.webdriver.chrome.options import Options
# define custom options for the Selenium driver
#options = Options()
# free proxy server URL
# proxy_server_url = "192.168.2.203:9999"
# options.add_argument(f'--proxy-server={proxy_server_url}')

options = webdriver.ChromeOptions()
options.add_argument('blink-settings=imagesEnabled=false')
options.add_argument('window-size=600,600')
#options.add_argument("--headless=new")
# options.add_argument('no-startup-window') 
# # If options.headless = True, the website will not load

# options.add_argument("--window-size=1920,1080")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# options.add_argument('--disable-blink-features=AutomationControlled')
# options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36')

#dr = webdriver.Chrome(options=options)


# chrome_options = uc.ChromeOptions()

# ## Disable loading images for faster crawling
# chrome_options.add_argument('--blink-settings=imagesEnabled=false')

# dr = uc.Chrome(options=chrome_options)

import redis  
import threading
# 创建Redis连接对象  
r = redis.Redis(host='192.168.2.203', port=6379, db=0,decode_responses=True)  
pending_check_url_list = "pending_check_url_list_newhot"
dealed_video_no_set = "dealed_video_no_set"

def crawl_video_contents():
    while True:
        try:
            url = r.lpop(pending_check_url_list)
            if url is None :
                print("pending_check_url_list队列已处理完")
                break
            dr = webdriver.Chrome(options=options)
            try:
                dr.get(url)
                bs = BeautifulSoup(dr.page_source, "html.parser")
                #如果未存在，先抓取seed信息，保存进数据库
                video_no = url.split('/')[len(url.split('/'))-1]
                #根据编号检查是否已经处理过
                video_no_index = video_no.lower().replace('-chinese-subtitle','').replace('-uncensored-leak','').replace('-','').replace('_','').replace(' ','')
                if r.sismember(dealed_video_no_set, video_no_index) > 0:
                    pass
                else:
                    hlsUrl = dr.execute_script('return window.source1280')
                    video_name = bs.find('title').text
                    seed = {}
                    seed["video_page_url"] = url
                    seed["video_m3u8_url"] = hlsUrl
                    seed["video_name"] = video_name
                    seed["video_no"]= video_no
                    params = [video_no,video_name,hlsUrl,url,'','crawl']
                    request.remote_call('p_check_save_seed',params)
                    r.sadd(dealed_video_no_set,video_no_index)
            except Exception as e:
                print(f"Error: {e}")
                r.rpush(pending_check_url_list,url)
            finally:
                try:
                    dr.quit()
                except:
                    pass

        except Exception as e:
            print(f"Error: {e}")
            r.rpush(pending_check_url_list, url)


import threading
import queue

# Use a queue to manage URLs
url_queue = queue.Queue()

# Create a thread pool
thread_pool = []


def crawl_video_links():
    while True:
        try:
            url = url_queue.get(timeout=1)
        except queue.Empty:
            print("队列已处理完毕")
            break

        #先爬取所有的url，放进pending列表中
        try:
            print(url)
            dr = webdriver.Chrome(options=options)
            dr.get(url)
            bs = BeautifulSoup(dr.page_source, "html.parser")
            a_all = bs.body.find_all('a')
            
            for a in a_all:
                if a is not None and a.get("class") is not None and a.get('class').count("text-secondary")>0:
                    if a is not None and a.get("href") is not None:
                        href = a.get('href')
                        if href.count("#") > 0 :
                            href = href.split('#')[0]
                        if re.match(url_pattern, href) and 'page=' not in href:
                            #href = "https://missav.com"+href
                            target_video_no = href.split('/')[len(href.split('/'))-1].replace('-uncensored-leak','')
                            target_video_no_index = target_video_no.lower().replace('-chinese-subtitle','').replace('-uncensored-leak','').replace('-','').replace('_','').replace(' ','')
                            if r.sismember(dealed_video_no_set,target_video_no_index) == 0 :
                                pos = r.lpos(pending_check_url_list,href)
                                if pos is None:
                                    r.rpush(pending_check_url_list, href)
        except Exception as e:
            print(f"Error: {e}")
            if 'page=' not in url:
                r.rpush(pending_check_url_list,url)
        finally:
            try:
                dr.quit()
            except:
                pass
        
        url_queue.task_done()

#Populate the URL queue
for p in range(448):
    #url = f"https://missav.com/dm206/en/monthly-hot?page={p}"
    #url = f"https://missav.com/dm509/en/new?page={p}"
    #url = f"https://missav.com/dm504/en/release?page={p}"
    url = f"https://missav.com/dm188/en/actors/Daisuke%20Sadamatsu?page={p}"
    url_queue.put(url)
    

MAX_THREADS = 12

#Create and start the worker threads
for _ in range(MAX_THREADS):
    worker = threading.Thread(target=crawl_video_links)
    thread_pool.append(worker)
    worker.start()

#Wait for all tasks to complete
url_queue.join()

#Wait for all threads to complete
for worker in thread_pool:
    worker.join()

print("collect links completed.")


for _ in range(MAX_THREADS):
    worker = threading.Thread(target=crawl_video_contents)
    thread_pool.append(worker)
    worker.start()

for worker in thread_pool:
    worker.join()

print("crawling contents complete")