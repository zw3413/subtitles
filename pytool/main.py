import sys
from download import download
from transcribe import transcribe
from t2tt import t2tt

class Unbuffered:
    def __init__(self, stream):
       self.stream = stream

    def write(self, data):
        try:        
            self.stream.write(data)
            self.stream.flush()
            te.write(data)    # Write the data of stdout here to a text file as well
            te.flush()
        except Exception as e:
            pass
    
    def flush(data):
        try:
            te.flush()
        except Exception as e:
            pass

current_directory = os.path.dirname(os.path.abspath(__file__))
te = open(current_directory+"/../file/log/subtitle.log",'a', encoding='utf-8')  # File where you need to keep the logs
sys.stdout=Unbuffered(sys.stdout)

def main(argv):
    cmd = argv[1]
    print("rukou")
    print(cmd)
    
    if cmd == "download":
        download()
    elif cmd == "transcribe":
        transcribe()
    elif cmd == "t2tt":
        t2tt()
    else :
        print("命令错误"+cmd)
    
if __name__ == "__main__" :
    main(sys.argv[0:])