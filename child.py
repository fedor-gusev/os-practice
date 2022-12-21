import os
import sys
import time
import random

pid = os.getpid()
ppid = os.getppid()
print(f"[Child {pid}]: I am started. PID {pid}. Parent PID {ppid}")
s = sys.argv[1]
time.sleep(int(s))
print(f"[Child {pid}]: I am ended. PID {pid}. Parent PID {ppid}")
sys.exit(random.randint(0, 1))
