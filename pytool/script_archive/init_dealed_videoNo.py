import csv  
import redis  
  
# 连接到Redis服务器  
r = redis.Redis(host='192.168.2.203', port=6379, db=0)  
  
# 设置Redis集合的key  
set_key = 'dealed_video_no_set'  
  
# 读取CSV文件并添加到Redis集合中  
def import_csv_to_set(csv_file_path, set_key):  
    with open(csv_file_path, 'r', encoding = 'utf-8') as csvfile:  
        reader = csv.reader(csvfile)  
        for row in reader:  
            # 假设CSV文件中的每一行只有一个字段，你想要添加到集合中  
            # 如果有多列，你需要决定哪一列或哪些列的组合是唯一的，并添加到集合中  
            element = row[0]  
            # 添加元素到Redis集合中  
            # 注意：集合中的元素是唯一的，所以重复的元素不会被添加  
            r.sadd(set_key, element)  
    print(f"Imported CSV data to Redis set '{set_key}'")  
  
# CSV文件路径  
csv_file_path = r"C:\\Users\\Elvin\\Desktop\\1.csv"
  
# 执行导入操作  
import_csv_to_set(csv_file_path, set_key)