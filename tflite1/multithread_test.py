import threading
import time

start=time.perf_counter()

def do_something():
    print('sleeping 1 seconds...')
    time.sleep(1)
    print('Done sleeping...')

while(1):
    t1 = threading.Thread(target=do_something)
    t1.start()
    
    print('testing')
    finish = time.perf_counter()
    t1.join()
    print(f'Finished in {round(finish-start,2)} second(s)')
    
