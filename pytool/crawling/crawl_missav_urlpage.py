import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import os
import json
import sys

# import undetected_chromedriver as uc

print(os.getcwd())
import sys

# sys.path.append(r'C:\\Developer\\Subtitles\\pytool\\')
sys.path.append(os.getcwd())
import request

url_pattern = re.compile(r"^.+/dm\d+/en/.+$")

# from selenium.webdriver.chrome.options import Options
# define custom options for the Selenium driver
# options = Options()
# free proxy server URL
# proxy_server_url = "192.168.2.203:9999"
# options.add_argument(f'--proxy-server={proxy_server_url}')

options = webdriver.ChromeOptions()
options.add_argument("blink-settings=imagesEnabled=false")
options.add_argument("window-size=600,600")
# options.add_argument("--headless=new")
# options.add_argument('no-startup-window')
# # If options.headless = True, the website will not load

# options.add_argument("--window-size=1920,1080")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# options.add_argument('--disable-blink-features=AutomationControlled')
# options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36')

# dr = webdriver.Chrome(options=options)


# chrome_options = uc.ChromeOptions()

# ## Disable loading images for faster crawling
# chrome_options.add_argument('--blink-settings=imagesEnabled=false')

# dr = uc.Chrome(options=chrome_options)
import time
import redis
import threading
import traceback
# 创建Redis连接对象
#r = redis.Redis(host="192.168.2.203", port=6379, db=0, decode_responses=True)
r = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)
pending_check_url_list = "pending_check_url_list_urlpage"
dealed_video_no_set = "dealed_video_no_set"

#接收参数列表
# full 全自动，先从索引页抓取视频页，然后遍历视频页抓取信息
# semi 半自动，直接遍历视频页抓取信息
mode = "full"
# all  抓取seed和jav信息
# seed 仅抓取seed信息
# jav  仅抓取jav信息
target = "all"


url_fortest = None

def removeNewline(eles):
    newEles = []
    for ele in eles:
        if ele != '\n':
            newEles.append(ele)
    return newEles

def crawl_video_contents():
    url = ""
    while True:
        try:
            if url_fortest is not None:
                url = url_fortest
            else:
                url = r.lpop(pending_check_url_list)
            if url is None:
                print("pending_check_url_list队列已处理完")
                break
            dr = webdriver.Chrome(options=options)
            try:
                dr.get(url)
                #WebDriverWait(dr, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
                bs = BeautifulSoup(dr.page_source, "html.parser")
                # 如果未存在，先抓取seed信息，保存进数据库
                video_no = url.split("/")[len(url.split("/")) - 1]
                # 根据编号检查是否已经处理过
                video_no_index = (
                    video_no.lower()
                    .replace("-chinese-subtitle", "")
                    .replace("-uncensored-leak", "")
                    .replace("-", "")
                    .replace("_", "")
                    .replace(" ", "")
                )
                if (
                    r.sismember(dealed_video_no_set, video_no_index) > 0
                    and url_fortest is None
                ):
                    pass
                else:
                    title_ele = bs.find("title")
                    for i in range(10):
                        if title_ele is  None:
                            time.sleep(5)
                            title_ele = bs.find("title")
                        else:
                            break
                    if title_ele is None :
                        raise Exception("没有获取到title元素")
                    video_name = title_ele.text
                    hlsUrl = dr.execute_script("return window.source1280")
                    if target in ["all","seed"]:
                        seed = {}
                        seed["video_page_url"] = url
                        seed["video_m3u8_url"] = hlsUrl
                        seed["video_name"] = video_name
                        seed["video_no"] = video_no
                        params = [video_no, video_name, hlsUrl, url, "", "crawl"]
                        request.remote_call("p_check_save_seed", params)

                    if target in ["all","jav"]:
                        jav = {}
                        jav["jav_no"] = video_no_index
                        jav["source"] = "missav.com"
                        try:
                            # get video description
                            description = ""
                            try:
                                desc_meta = bs.find(
                                    "meta", property="og:description"
                                )
                                if desc_meta is not None:
                                    description = desc_meta.get("content")
                            except Exception as e:
                                print("001", e)
                            if description == "":
                                try:
                                    desp_ele = description = bs.find(
                                        "div",
                                        class_="mb-1 text-secondary break-all line-clamp-2",
                                    )
                                    if desp_ele is not None:
                                        description = desp_ele.text

                                except Exception as e:
                                    print("002", e)
                            jav["description"] = description
                        except Exception as e:
                            print("extract description failed")
                            print(e)

                        try:
                            image_ele = bs.find("meta", property="og:image")
                            if image_ele is not None:
                                jav["image1"] = image_ele.get(
                                    "content"
                                )
                        except Exception as e:
                            print("extract image1 failed")
                            print(e)

                        try:
                            video_length_ele = bs.find(
                                "div", class_="plyr__time--duration"
                            )
                            if video_length_ele is not None :
                                jav["video_length"] = video_length_ele.text
                        except Exception as e:
                            print("extract video_length failed")
                            print(e)

                        try:
                            detail = bs.find("div", class_="space-y-2")
                            detail_eles = []
                            for i in range(10):
                                if detail is  None:
                                    time.sleep(5)
                                    detail = bs.find("div", class_="space-y-2")
                                else:
                                    break
                            if detail is not None :
                                detail_eles = detail.contents
                                eles = []
                                delimiter = ","
                                for item in detail_eles:
                                    if item != "\n":
                                        eles.append(item)
                                if len(eles) > 0:
                                    for i in range(len(eles)):
                                        first_span = eles[i].contents[0]
                                        contents = removeNewline(eles[i].contents)
                                        second_ele = contents[1] if len(contents) >= 2 else None
                                        if first_span is not None and second_ele is not None:
                                            first_span_text = first_span.text.strip()
                                            if first_span_text == "Release date:":
                                                jav["publish_time"] = second_ele.text.strip()
                                            elif first_span_text == "Title:":
                                                jav["jav_name"] = second_ele.text.strip()
                                            elif first_span_text == "Actress:":
                                                infos = []
                                                for t in eles[i].find_all("a"):
                                                    if t is not None:
                                                        infos.append(t.text)
                                                jav["actress_1"] = delimiter.join(infos)
                                            elif first_span_text in ["Genre:","Tag:"]:
                                                infos = []
                                                for t in eles[i].find_all("a"):
                                                    if t is not None and t.text != "Uncensored Leak":
                                                        infos.append(t.text)
                                                jav["tag"] = delimiter.join(infos)
                                            elif first_span_text == "Maker:":
                                                infos = []
                                                for t in eles[i].find_all("a"):
                                                    if t is not None:
                                                        infos.append(t.text)
                                                jav["publisher"] = delimiter.join(infos)
                                            elif first_span_text == "Director:":
                                                infos = []
                                                for t in eles[i].find_all("a"):
                                                    if t is not None:
                                                        infos.append(t.text)
                                                jav["director"] = delimiter.join(infos)
                        except Exception as e:
                            print("extract jav detail failed")
                            tb = traceback.format_exc()
                            print("Traceback: ", tb)
                            raise e

                        params = [json.dumps(jav)]
                        result = request.remote_call("p_save_javlibrary", params)
                        if result["rc"] != "000":
                            print(result["rc"], result["rm"])
                            print("保存jav失败")
                            r.rpush(pending_check_url_list, url)
                    r.sadd(dealed_video_no_set, video_no_index)
            except Exception as e:
                print(f"抓取信息发生异常: {e}")
                tb = traceback.format_exc()
                print("Traceback: ", tb)
                r.rpush(pending_check_url_list, url)
            finally:
                try:
                    dr.quit()
                except:
                    pass

        except Exception as e:
            print(f"处理当前url失败: {e}")
            print(url)
            r.rpush(pending_check_url_list, url)
        finally:
            if url_fortest is not None:
                break


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

        # 先爬取所有的url，放进pending列表中
        try:
            print(url)
            dr = webdriver.Chrome(options=options)
            dr.get(url)
            bs = BeautifulSoup(dr.page_source, "html.parser")
            a_all = bs.body.find_all("a")

            for a in a_all:
                if (
                    a is not None
                    and a.get("class") is not None
                    and a.get("class").count("text-secondary") > 0
                ):
                    if a is not None and a.get("href") is not None:
                        href = a.get("href")
                        if href.count("#") > 0:
                            href = href.split("#")[0]
                        if re.match(url_pattern, href) and "page=" not in href:
                            # href = "https://missav.com"+href
                            target_video_no = href.split("/")[
                                len(href.split("/")) - 1
                            ].replace("-uncensored-leak", "")
                            target_video_no_index = (
                                target_video_no.lower()
                                .replace("-chinese-subtitle", "")
                                .replace("-uncensored-leak", "")
                                .replace("-", "")
                                .replace("_", "")
                                .replace(" ", "")
                            )
                            if (
                                r.sismember(dealed_video_no_set, target_video_no_index)
                                == 0
                            ):
                                pos = r.lpos(pending_check_url_list, href)
                                if pos is None:
                                    r.rpush(pending_check_url_list, href)
        except Exception as e:
            print(f"Error: {e}")
            if "page=" not in url:
                r.rpush(pending_check_url_list, url)
        finally:
            try:
                dr.quit()
            except:
                pass

        url_queue.task_done()


class Page:
    def __init__(self, url, pages):
        self.url = url
        self.pages = pages


default_pages = 500


def start_auto_crawling():
    MAX_THREADS = 1
    if mode =="full":
        # collect video urls
        index_page = [
            # Page("https://missav.com/dm30/en/actresses/Kana%20Mito", 12),
            # Page("https://missav.com/dm38/en/labels/Madonna", 649),
            # Page("https://missav.com/dm188/en/actors/Daisuke%20Sadamatsu", default_pages),
            # Page("https://missav.com/dm206/en/monthly-hot", default_pages),
            # Page("https://missav.com/dm509/en/new", default_pages),
            # Page("https://missav.com/dm504/en/release", default_pages),
            Page("https://missav.com/dm25/en/actresses/Remu%20Suzumori",3)
        ]

        for page in index_page:
            print("start to crawling", page.url, page.pages)
            # Populate the URL queue
            for p in range(page.pages):
                # url = f"https://missav.com/dm206/en/monthly-hot?page={p}"
                # url = f"https://missav.com/dm509/en/new?page={p}"
                url = f"{page.url}?page={p}"
                url_queue.put(url)



            # Create and start the worker threads
            for _ in range(MAX_THREADS):
                worker = threading.Thread(target=crawl_video_links)
                thread_pool.append(worker)
                worker.start()

            # Wait for all tasks to complete
            url_queue.join()

            # Wait for all threads to complete
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

    elif mode == "semi":
        # crawling video infos
        for _ in range(MAX_THREADS):
            worker = threading.Thread(target=crawl_video_contents)
            thread_pool.append(worker)
            worker.start()

        for worker in thread_pool:
            worker.join()

        print("crawling contents complete")


# start_auto_crawling()

# crawl_video_contents("https://missav.com/dm39/en/juq-175-uncensored-leak")

if __name__ == "__main__":

    if len(sys.argv) > 2:
        arguments = sys.argv[1:]
        print("参数", arguments)
        [mode, target] = arguments
    else:
        print("没有输入参数, 使用默认参数", mode, target)


    start_auto_crawling()


    print("结束")
