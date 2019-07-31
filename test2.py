import numpy as np
import time
if __name__ == "__main__":

    start = time.time()
    for _ in range(100000000):
        pass
    end = time.time()
    print("循环运行时间:%.2f秒" % (end - start))
    # output:循环运行时间:5.50秒