# -*- coding: utf-8 -*-

import requests
import json
import logging

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
    datefmt="## %Y-%m-%d %H:%M:%S",
)

logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger()
logger.info("开始加载")
# serverIp = "https://api.subtitlex.xyz"
serverIp = "http://192.168.2.203:12801"


# serverIp = "http://192.168.2.203:12801"
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
        response = requests.post(
            serverIp + "/common/allPurpose", headers=headers, data=json.dumps(data)
        )
        if response.status_code == 200:
            return response.json()
        else:
            # TODO: 显示调用失败的消息给用户
            logger.error(f"Call failed with status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        # TODO: 显示调用失败的消息给用户
        logger.error(f"Call failed: {e}")
        return None


def getSeedNeedProcess(type):
    pl = [type]
    logger.info("remote_call p_get_need_process")
    result = remote_call("p_get_need_process", pl)
    logger.info(result)
    if result["rc"] == "000":
        return json.loads(result["data"])
    else:
        return None


def SaveSeed(seed):
    try:
        url = serverIp + "/save_seed"
        # print("SaveSeed:")
        # print(seed)
        r = requests.post(url, json=seed, timeout=60)
        jData = json.loads(r.text)
        return jData
    except Exception as e:
        logger.error(e)
        return


def SaveSubtitle(subtitle):
    try:
        url = serverIp + "/save_subtitle"
        # print("SaveSubtitle:")
        # print(subtitle)
        r = requests.post(url, json=subtitle, timeout=60)
        jData = json.loads(r.text)
        return jData
    except Exception as e:
        logger.error(e)
        return


def upload_file(file_path, url):
    with open(file_path, "rb") as file:
        files = {"file": file}
        response = requests.post(url, files=files)

        if response.status_code == 200:
            logger.info("File uploaded successfully!")
        else:
            logger.error("Failed to upload file. Status code:", response.status_code)
            logger.error("Response:", response.text)


def PushSubtitleToServer(tgt_path, file_name):
    upload_url = serverIp + "/upload-files?filename=" + file_name
    file_path = tgt_path
    upload_file(file_path, upload_url)


import os
import subprocess

filePath_prefix_video = "/content/file/video/"
os.makedirs(filePath_prefix_video, exist_ok=True)
FLV_afterfix = ".flv"


def downloadFlv(url, filePath, quality="worst"):
    threads = "10"
    origin = ""
    quality = quality  # "worst"
    # fileName =  hashlib.md5(url.encode()).hexdigest() +FLV_afterfix
    # match = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", url)
    # if match != None:
    #     fileName = match.group(0)+FLV_afterfix

    # delete the file at filePath if exist
    if os.path.exists(filePath):
        os.remove(filePath)
    cmd = (
        "streamlink --retry-max 3 --retry-streams 3 --stream-segment-attempts 20 --stream-segment-timeout 60 --stream-timeout 120 --http-timeout 120 --stream-segment-threads "
        + threads
        + ' -o "'
        + filePath
        + '" --http-header "User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 AOL/9.8 AOLBuild/4346.2019.US Safari/537.36" --http-header "Origin='
        + origin
        + '" "hlsvariant://'
        + url
        + '" '
        + quality
    )
    logger.info(cmd)
    # output = os.system(cmd)
    logger.info("调用subprocess.call执行streamlink命令")
    command_result = subprocess.call(cmd, shell=True)
    logger.info("调用subprocess.call执行streamlink命令结束，返回" + str(command_result))
    return command_result
    # return 0,fileName


# quality = 'worst'
# video_m3u8_url = r'https://surrit.com/0e779002-2042-4e42-9d59-c2780fabaaac/842x480/video.m3u8'
# output, flvPath = downloadFlv(video_m3u8_url,quality)
# print(output)
# print(flvPath)

from faster_whisper import WhisperModel
from datetime import timedelta, datetime
import torch

compute_type = "float16" if torch.cuda.is_available() else "int8"

model_size = "large-v3"  # "base" #
model_path = r"C:\Users\Wei Zhang\.cache\huggingface\hub\models--Systran--faster-whisper-large-v3\snapshots\edaa852ec7e145841d8ffdb056a99866b5f0a478"
device = "cuda" if torch.cuda.is_available() else "cpu"
# logger.info("开始加载fast-shisper model " +device)
# model = WhisperModel(
#     model_path,
#     #model_size,
#     device = device ,
#     compute_type= compute_type,
#     local_files_only = False,
# )
# logger.info("加载fast-whisper model完成")
filePath_prefix_srt = "/content/file/subtitle/"
os.makedirs(filePath_prefix_srt, exist_ok=True)
SRT_afterfix = ".srt"

import sys

sys.path.append("/content/drive/MyDrive/Subtitles/pytool")
import utils


def transcribe_func(flvPath, model, thread_name=""):
    segments, info = model.transcribe(
        filePath_prefix_video + flvPath, beam_size=5, vad_filter=True, task="transcribe"
    )
    print(
        "Detected language '%s' with probability %f"
        % (info.language, info.language_probability)
    )
    if info.language_probability < 0.85:  # 如果语言预测的可能性小于0.9，强制使用ja
        segments, info = model.transcribe(
            filePath_prefix_video + flvPath,
            beam_size=5,
            vad_filter=True,
            #vad_parameters=dict(min_silence_duration_ms=1000),
            language="ja",
            task="transcribe",
        )
        print(
            "Detected language '%s' with probability %f"
            % (info.language, info.language_probability)
        )
    language = info.language
    file_name = (
        flvPath.replace(FLV_afterfix, SRT_afterfix)
        .replace("_worst", "")
        .replace("_best", "")
    )
    srtPath = filePath_prefix_srt + file_name
    if os.path.exists(srtPath):
        os.remove(srtPath)
    f = open(srtPath, "w", encoding="utf-8")
    lineCount = 0
    t_start = datetime.now()
    pt = ""
    print(thread_name)
    for segment in segments:
        lineCount += 1
        f.write(str(lineCount) + "\n")
        s = utils.secondsToStr(segment.start)
        e = utils.secondsToStr(segment.end)
        f.write(s + " --> " + e + "\n")
        t = e.split(",", 1)[0].replace(":", "")[0:3]
        if t != pt:
            print(t, end=" ")
            pt = t
        f.write(segment.text)
        f.write("\n\n")
        lineCount = lineCount + 1
    f.flush()
    f.close()
    return srtPath, file_name, language


# srtPath, file_name = transcribe_func('0e779002-2042-4e42-9d59-c2780fabaaac.flv')
# print(srtPath)
# print(file_name)
import threading
import time
import queue


def executeDownload(q):
    logger.info("executeDownload thread start")

    while True:
        while not q.empty():  # 等待transcribe取走已经下载好的seed
            time.sleep(1)

        seed = getSeedNeedProcess("download_transcribe")
        if seed is None:
            break  # 结束生产者
        try:
            seed["id"] = str(seed["id"])
            video_m3u8_url = seed["video_m3u8_url"]
            uuid = seed["uuid"]
            quality = "worst"
            logger.info("开始下载" + seed["id"])
            flvPath = uuid + FLV_afterfix
            filePath = filePath_prefix_video + flvPath

            # 第一次下载使用变换过的url
            original_video_m3u8_url = ""
            if (
                "720p" in video_m3u8_url
                or "1280x720" in video_m3u8_url
                or "1080p" in video_m3u8_url
                or "720x1280" in video_m3u8_url
            ):
                original_video_m3u8_url = video_m3u8_url
                video_m3u8_url = (
                    video_m3u8_url.replace("720p", "480p")
                    .replace("1080p", "480p")
                    .replace("1280x720", "842x480")
                    .replace("720x1280", "842x480")
                )
                print(f"modify m3u8 url from %s, to %s" %( original_video_m3u8_url, video_m3u8_url) )
            output = downloadFlv(video_m3u8_url, filePath, quality)
            if output != 0:
                # 如果第一次下载失败，使用原始url再尝试一次
                if original_video_m3u8_url != "":
                    print(f"use original url try again %s" % original_video_m3u8_url)
                    video_m3u8_url = original_video_m3u8_url
                    output = downloadFlv(video_m3u8_url, filePath, quality)
                    if output != 0:
                        logger.info("下载失败" + str(output))
                        seed["process_status"] = "8e"
                        seed["err_msg"] = "下载失败" + str(output)
                        SaveSeed(seed)
                    else:
                        q.put((seed, flvPath))  # 放入队列
                        logger.info("下载完成 " + str(seed["id"]))
                else:
                    logger.info("下载失败" + str(output))
                    seed["process_status"] = "8e"
                    seed["err_msg"] = "下载失败" + str(output)
                    SaveSeed(seed)
            else:
                q.put((seed, flvPath))  # 放入队列
                logger.info("下载完成 " + str(seed["id"]))
        except Exception as e:
            logger.error("下载异常" + str(e))
            seed["process_status"] = "8e"
            seed["err_msg"] = "下载异常" + str(e)
            SaveSeed(seed)
    logger.info("executeDownload thread end")


def executeTranscribe(q, thread_name):
    logger.info(thread_name + " executeTranscribe thread start")
    logger.info(thread_name + " 开始加载fast-shisper model ")
    global model_path, device, compute_type
    model = WhisperModel(
        model_path,
        # model_size,
        device=device,
        compute_type=compute_type,
        local_files_only=False,
    )
    logger.info(thread_name + " 加载fast-whisper model完成")
    while True:
        try:
            seed, flv_path = q.get(
                block=False
            )  # 非阻塞获取，如果队列为空则抛出异常 #comment 1
            # seed ={} #comment 1
        except queue.Empty:  # 队列为空，等待1s再试
            time.sleep(1)
            continue

        if seed is None:  # 收到终止信号
            logger.info(
                thread_name + " seed is None, exit the executeTranscribe thread"
            )
            break

        try:
            logger.info(thread_name + " transcribe 开始转译")
            # flv_path = 'f3b71bbc-d624-46bc-9504-9754be9e20b7.flv' #comment 1
            srtPath, file_name, language = transcribe_func(flv_path, model, thread_name)
            logger.info(thread_name + " transcribe 转译结束")
            PushSubtitleToServer(srtPath, file_name)  # srt文件推送到服务器
            seed["srt_path"] = srtPath.replace(filePath_prefix_srt, "")
            seed["video_language"] = language
            seed["process_status"] = "8"
            seed["err_msg"] = ""
            SaveSeed(seed)
            subtitle = {}
            subtitle["language"] = utils.language_codes[language]
            subtitle["path"] = srtPath.replace(filePath_prefix_srt, "")
            subtitle["seed_id"] = seed["id"]
            subtitle["format"] = SRT_afterfix
            SaveSubtitle(subtitle)
            if os.path.exists(filePath_prefix_video + flv_path):
                os.remove(filePath_prefix_video + flv_path)
                logger.info(
                    thread_name + " 移除视频文件" + filePath_prefix_video + flv_path
                )
        except Exception as e:
            logger.error(thread_name + " 转译异常" + str(e))
            seed["process_status"] = "8e"
            seed["err_msg"] = "转译异常" + str(e)
            SaveSeed(seed)
        finally:
            q.task_done()
    logger.info(thread_name + " executeTranscribe thread end")


logger.info("完成加载")


def main():
    q = queue.Queue(maxsize=1)

    download_thread = threading.Thread(target=executeDownload, args=(q,))
    download_thread.start()  # comment 1

    # time.sleep(2)
    # download_thread_1 = threading.Thread(target=executeDownload, args=(q,))
    # download_thread_1.start()  # comment 1

    transcribe_thread_1 = threading.Thread(
        target=executeTranscribe, args=(q, "transcribe_thread_1")
    )
    transcribe_thread_1.start()

    # transcribe_thread_2 = threading.Thread(target=executeTranscribe, args=(q,'transcribe_thread_2'))
    # transcribe_thread_2.start()

    # 等待生产者线程结束
    download_thread.join()  # comment 1
    #download_thread_1.join()
    q.join()
    q.put((None, None))
    # q.put((None,None))
    transcribe_thread_1.join()
    # transcribe_thread_2.join()


if __name__ == "__main__":
    main()
