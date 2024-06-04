import os , re , sys

print(os.getcwd())
sys.path.append(os.getcwd())
import request

directory_path = './scripts/file/字幕包/JavSubsCh'  # 替换为你的目录路径  
pattern_video_no_1 = re.compile(r'^[@,gachi]?([a-zA-Z\d{6}]+(_hd)?[-_\s]?S?[0-9]+)\s*.*\.([a-zA-Z]+)$')
file_count = 0 
unrecognized_count = 0

def get_all_files(directory):  
    global unrecognized_count, file_count, pattern_video_no_1
    # 遍历目录中的文件  
    for name in os.listdir(directory):  
        path = os.path.join(directory, name)  
        # 如果是目录，则递归遍历  
        if os.path.isdir(path):  
            get_all_files(path)  
        # 如果是文件，则添加到列表中  
        elif os.path.isfile(path):  
            file_count += 1
            match = pattern_video_no_1.match(name)
            if match:
                video_no = match.group(1)
                if video_no is None:
                    print("没有识别到video_no，请关注", end=" ")
                    print(path)
                language = 'detect_cmn'
                ext = match.group(3)
                filename = name
                filepath = path.replace('./scripts/file/','')
                params = [video_no, language, ext, filename,filepath]
                request.remote_call('p_save_zmbsubtitles',params)
            else:
                print(f"正则未匹配上，请关注 {path}")
                unrecognized_count += 1
  
all_files = get_all_files(directory_path)  
print(f"共有文件{file_count}个")
print(f"未识别文件{unrecognized_count}个")