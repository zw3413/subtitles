import os
import sys
print(os.getcwd())
sys.path.append(os.getcwd())
from utils import *

def get_text_files_in_folder(folder_path):
    text_files = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".srt"):
            text_files.append(os.path.join(folder_path, filename))
    return text_files

#给没有行号的添加行号
def process_text_files_1(folder_path): 
    text_files = get_text_files_in_folder(folder_path)
    for file_path in text_files:
        try:
            addLineNumber(file_path)
            pass
        except Exception as e:
            print(file_path)
            print(e)


#处理缺少换行的情况
def process_text_files(folder_path, regex_pattern):
    text_files = get_text_files_in_folder(folder_path)
    for file_path in text_files:
        try:
            modify_lines_in_file(file_path, regex_pattern)
        except Exception as e:
            print(file_path)
            print(e)
            pass

import re

def modify_lines_in_file(file_path, regex_pattern):
    modified_lines = []
    with open(file_path, "r",encoding='utf-8') as file:
        for line in file:
            match = re.match(regex_pattern, line)
            if match:
                print(file_path)
                print(line)
                short_pattern = r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}"
                short_match = re.match(short_pattern , line)
                modified_line = line.replace (short_match.group(), f"{short_match.group()}\n")
                modified_lines.append(modified_line)
                print(modified_line)
            else:
                modified_lines.append(line)

    # Write the modified lines back to the file
    with open(file_path, "w", encoding='utf-8') as file:
        file.writelines(modified_lines)

def addLineNumber(file_path):
    regex_pattern_timestamp = r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$"
    regex_pattern_number = r'^-?\d+$'
    modified_lines = []
    pre_line = ""
    line_count = 0
    changedFlag = False
    encoding = detect_encoding(file_path)
    with open(file_path, "r",encoding=encoding) as file:
        for line in file:
            match_current = re.match(regex_pattern_timestamp, line.strip())
            match_previou = re.match(regex_pattern_number,pre_line.strip())
            if match_current and not match_previou:
                changedFlag = True
                line_count += 1
                addedLine = str(line_count)
                modified_lines.append(addedLine+'\n')
                # print(file_path)
                # print(addedLine)
                # print(line)
            modified_lines.append(line)
            if len(line.strip())>0 :
                pre_line = line

    if changedFlag:
        print(file_path)
        # Write the modified lines back to the file
        with open(file_path, "w+", encoding='utf-8') as file:
            file.writelines(modified_lines)

def file_line_count_greater_2(file_path):
    line_count = 0 
    encoding = detect_encoding(file_path)
    with open(file_path, "r",encoding=encoding) as file:
        for line in file:
            if line_count >=2 :
                return True
            line_count+=1

 
def find_possible_issue_1(file_path):
    text_files = get_text_files_in_folder(folder_path)
    for file_path in text_files:
        try:
            if(not file_line_count_greater_2(file_path)):
                print(file_path)
        except Exception as e:
            print(file_path)
            print(e)
            pass
# Example usage:
folder_path = r"C:\Developer\Subtitles\file\subtitle"
regex_pattern = r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}.+$"
#process_text_files(folder_path, regex_pattern) #打断时间戳与内容连起来的情况
#process_text_files_1(folder_path)  #添加数字行号，但是一些小语种例如rus等 格式还是有好多混乱
find_possible_issue_1(folder_path)