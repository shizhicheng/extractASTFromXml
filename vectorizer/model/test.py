from vectorizer.model.samplingTest import *
import time
from vectorizer.model.constVariable import *

if __name__=="__main__":
    # with open(leaveDicPath,"rb") as f:
    #     leaveDic=pickle.load(f)
    # with open(methodNameDicPath,"rb") as f:
    #     methodNameDic=pickle.load(f)
    #
    #
    # # 定义输入数据，sample操作
    # sample_gen = batchSamples(BATCH_SIZE,leaveDic,methodNameDic)
    #
    # start=time.time()
    # for sample in sample_gen:
    #     print(sample)
    #     end=time.time()
    #     print(end-start)
    array=np.zeros(100*24222*233)
    array=array.reshape(100,24222,233)
    print(array)

