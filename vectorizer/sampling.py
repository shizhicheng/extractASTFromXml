from vectorizer.nodeMap import nodeMap
from vectorizer.parameters import dataPath, samplePath
import pickle
import numpy as np
import sys

'''
获得批处理数据
'''


# 根据根节点获得（parent，child）
def getParentChildPair(root, pairList):
    for node in root:
        tup = (root.tag, node.tag)
        pairList.append(tup)
        getParentChildPair(node, pairList)
    return pairList


# 获得文件中所有（parent，child)，并序列化写入外存
def getAllPair(readFrom, writeTo):
    with open(readFrom, 'rb') as f:
        data = pickle.load(f)
        count = 1
        list = []
        while data != None:
            root = data[1]
            tempList = []
            list += getParentChildPair(root, tempList)

            # 打印已处理节点的个数
            if count % 10000 == 0:
                print("已经处理了" + str(count) + "节点")
            count += 1
            try:
                data = pickle.load(f)
            except EOFError:
                break

        # 打印sample的个数
        print(len(list))

        # 将列表序列化写入外存
        with open(writeTo, "wb") as f:
            pickle.dump(list, f)
        return list


# 获得批处理数据
def batchSamples(samples, batchSize):
    batch = ([], [])
    count = 0
    indexOf = lambda x: nodeMap[x]
    for sample in samples:
        batch[0].append(indexOf(sample[0]))
        batch[1].append(indexOf(sample[1]))
        count += 1
        if count >= batchSize:
            yield batch
            batch, count = ([], []), 0


# path指定外存路径
# sampleType指定是训练，验证，测试，3:1:1比例
def getSamples(path, sampleType):
    with open(path, 'rb') as f:
        samples = pickle.load(f)
        samplesLen = len(samples)
        samples = np.asarray(samples)

        if sampleType is "train":
            samples = samples[:int(0.6 * samplesLen)]
        elif sampleType is "validate":
            samples = samples[int(0.6 * samplesLen): int(0.8 * samplesLen)]
        elif sampleType is "test":
            samples = samples[int(0.8 * samplesLen):]
    return samples



# print(samples)
