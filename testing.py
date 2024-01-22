import time

start_time = time.time()
while True:
    if (time.time() - start_time) > 5:
        print("abc")
        start_time = time.time()
    
