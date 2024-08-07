#ffmpeg -i "input.mp4" -c:v libx264 -tag:v avc1 -movflags faststart -crf 30 -preset superfast "output.mp4"
import os

#folder_path = r"f:\\abc"
folder_path = r"C:\Users\Elvin\Developer"

def rename_file(old_name, new_name):
    try:
        os.rename(old_name, new_name)
        print(f"File renamed successfully from '{old_name}' to '{new_name}'")
        return True
    except FileNotFoundError:
        print(f"Error: The file '{old_name}' does not exist.")
        return False
    except FileExistsError:
        print(f"Error: A file with the name '{new_name}' already exists.")
        return False
    except PermissionError:
        print("Error: You don't have permission to rename this file.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

for filename in os.listdir(folder_path):
    if filename.endswith(".flv"):
        original_input_file = os.path.join(folder_path, filename)
        input_file = f"{os.path.splitext(original_input_file)[0]}_input.mp4"
        flag = rename_file(original_input_file, input_file)
        if not flag :
            print("rename the input filename error")
            continue
        output_file =  f"{os.path.splitext(input_file)[0]}_output.mp4"

        result = 0
        try:
            result = os.system(f"ffmpeg -i \"{input_file}\" -c:v libx264 -tag:v avc1 -movflags faststart -crf 30 -preset superfast \"{output_file}\"")
        except Exception as e:
            print("compress exception "+filename)
            print(e)
            continue
        
        if result != 0:
            print("compress error "+filename)
            continue
        
        flag = rename_file(output_file, original_input_file)
        if not flag :
            print("rename the output to original filename error")
            continue
        try:
            os.remove(input_file)
        except Exception as e:
            print("remove input file failed")
            print(e)

print("done")


