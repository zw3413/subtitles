print("import download.py")
from download import download_func
print("import transcribe.py")
from transcribe import transcribe_func
print("import t2tt.py")
from t2tt import t2tt_func
print("import ...")
import time
import threading
import sys
import os

class Unbuffered:
    def __init__(self, stream):
       self.stream = stream

    def write(self, data):
        try:        
            self.stream.write(data)
            self.stream.flush()
            te_4.write(data)    # Write the data of stdout here to a text file as well
            te_4.flush()
        except Exception as e:
            pass
    
    def flush(data):
        try:
            te_4.flush()
        except Exception as e:
            pass
        
current_directory = os.path.dirname(os.path.abspath(__file__))
te_4 = open(current_directory+"/../file/log/subtitle.log",'a', encoding='utf-8')  # File where you need to keep the logs
sys.stdout=Unbuffered(sys.stdout)

def thread01(args):
    while True:
        try:
            download_func()
        finally:
            time.sleep(2)
            

def thread02(args):
    while True:
        try:
            transcribe_func()
            t2tt_func()
        finally:
            time.sleep(2)

print("start threads")       
threads=[]
##注意一定args=(u'one',)  一个参数时候一定要加上,
##传入的参数要求是tuple，在python用(1,)表示一个tuple
t1=threading.Thread(target=thread01,args=(u'one',))
t2=threading.Thread(target=thread02,args=(u'two',))
threads.append(t1)
threads.append(t2)
for i in threads:
    # i.setDaemon(True)
    i.start()
