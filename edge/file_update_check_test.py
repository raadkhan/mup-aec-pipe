import os
import time
path = './tflite1/encoded_string.txt'

status = os.stat(path)
previous_time=0

while(previous_time != status.st_mtime_ns):
    print(status.st_mtime_ns)
    previous_time=status.st_mtime_ns
    time.sleep(5)
    
