import os

def get_text_files_in_folder(folder_path):
    """
    Returns a list of text files in the specified folder.
    """
    text_files = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".srt"):
            text_files.append(os.path.join(folder_path, filename))
    return text_files
def process_text_files_1(folder_path, regex_pattern):
    text_files = get_text_files_in_folder(folder_path)
    pass
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
    """
    Modifies lines in the specified file based on the regex pattern.
    """
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

# Example usage:
folder_path = r"C:\Developer\Subtitles\file\subtitle"
regex_pattern = r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}.+$"
#process_text_files(folder_path, regex_pattern)

regex_pattern_1 = r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$"
process_text_files_1(folder_path, regex_pattern_1)