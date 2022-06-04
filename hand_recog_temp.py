from sys import stdout
import time
import sys

count = 0

while(True):
    if count % 5 == 0:
        sys.stdout.write('J')
    else:
        sys.stdout.write('R')
    count += 1 
    sys.stdout.flush()
    time.sleep(1)
