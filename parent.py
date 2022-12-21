import os
import sys
import random

my_pid = os.getpid()


def process_with_children():
    pid = os.fork()
    if pid == 0:
        # we are child
        os.execl("./child.py", "child", str(random.randint(5, 10)))
    print(f"Parent [{my_pid}]: I ran children process with PID {pid}")


# run specified number of children
n = int(sys.argv[1])
for i in range(0, n):
    process_with_children()

# wait for all children to finish
while n > 0:
    child_pid, status = os.wait()
    status = int(status / 256)
    print(f"Parent[{my_pid}]: Child with PID {child_pid} terminated. Exit Status {status}.")
    if status != 0:
        process_with_children()
    else:
        n = n - 1
