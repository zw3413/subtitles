import os

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
            addLineNumber(file_path,regex_pattern_timestamp)
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
    with open(file_path, "r",encoding='utf-8') as file:
        for line in file:
            match_current = re.match(regex_pattern_timestamp, line.strip())
            match_previou = re.match(regex_pattern_number,pre_line.strip())
            if match_current and not match_previou:
                print(file_path)
                print(line)
                line_count += 1
                addedLine = str(line_count)
                modified_lines.append(addedLine)
                print(addedLine)
            else:
                modified_lines.append(line)
    
            if len(line.strip())>0 :
                pre_line = line

    # Write the modified lines back to the file
    with open(file_path, "w+", encoding='utf-8') as file:
        file.writelines(modified_lines)
    pass

# Example usage:
folder_path = r"C:\Developer\Subtitles\file\subtitle"
regex_pattern = r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}.+$"
#process_text_files(folder_path, regex_pattern)


process_text_files_1(folder_path)