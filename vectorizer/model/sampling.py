from vectorizer.model.config import BATCH_SIZE
from ExtractStatement.ExtractStatement import *
import pickle
from vectorizer.nodeMap import nodeMap
import re
import copy


def makeDataSet(leaveDicPath, methodNameDicPath, dataPath):
    # leaveDicPath = "..\\data\\dictionary\\leaveDic.data"
    # methodNameDicPath = "..\\data\\dictionary\\methodNameDic.data"
    #
    # # 数据存放的路径(methodName,root)
    # dataPath = "I:\\data\\batchReplaceFunctionName.data"

    # 获得批处理数据,方法名和方法体
    def batchSamples(path):
        with open(path, "rb") as f:
            batch = ([], [])
            data = pickle.load(f)
            count = 0
            while data != None:
                batch[0].append(data[0])
                batch[1].append(data[1])
                count += 1
                try:
                    data = pickle.load(f)
                except EOFError:
                    break
                if count >= BATCH_SIZE:
                    yield batch
                    batch, count = ([], []), 0

    # 获得所有叶子节点
    # root:根节点
    # path:叶子节点的字典
    def getAllleave(root, path):
        with open(path, "rb") as f:
            leaveDic = pickle.load(f)
        leaveList = []
        if root.text != None:
            # 对叶子节点进行分词，词性还原(默认将大写还原成小写)
            rootText = root.text
            # 分词
            pattern = re.compile(r'[A-Z][A-Z]+|[a-z]+|[A-Z]{1}[a-z]*')
            subTokens = pattern.findall(rootText)

            # 提取词干并转化成该词的编号
            for token in subTokens:
                token = token.lower()
                leaveList.append(leaveDic[token])
        for node in root:
            getAllleave(node, leaveDicPath)

    # 获得所有中间节点
    def getAllMidNode(root):
        midNodeList = []
        midNodeList.append(nodeMap[root.tag])
        for node in root:
            getAllleave(node, leaveDicPath)

    # 获得方法名的subtoken序列
    def getAllMethodNameSubToken(methodName, path):
        with open(path, "rb") as f:
            methodNameDic = pickle.load(f)

            # 分词
            pattern = re.compile(r'[A-Z][A-Z]+|[a-z]+|[A-Z]{1}[a-z]*')
            subTokens = pattern.findall(methodName)

            # 提取词干并转化成该词的编号
            methodNameList = []
            for token in subTokens:
                token = token.lower()
                methodNameList.append(methodNameDic[token])

            # 获得trgInput,trgLabel
            trgInput = copy.deepcopy(methodNameList)
            trgInput.insert(0, methodNameDic["sos"])

            trgLabel = copy.deepcopy(methodNameList)
            trgLabel = trgLabel.append(methodNameDic["eos"])

        return trgInput, trgLabel

    # 将抽象语法树分为中间节点以及叶子节点作为输入
    def generateSample(rootList, methondNameList):
        batchSize = len(rootList)

        samples = [([], [], None), ([], [], None)]

        # batchsize个语法树切分成的Statement子树列表
        batchSTs = [([], [], None)]
        for root in rootList:
            # 将单个语法树切分成多个statement子树
            STs = extractSTBaseRoot(root)

            midNodesList = []
            leaveList = []
            for node in STs:
                # 遍历树获得中间节点，并转化成编号
                midNodesList = getAllMidNode(node)

                # 遍历获得所有的叶子节点并进行分词，并转化成编号
                leaveList = getAllleave(node, leaveDicPath)

            batchSTs.append((midNodesList, leaveList, len(STs)))

        # 对方法进行处理，若方法名分词得到ABC，则处理得到两种形式的数据表示：
        # <sos>ABC  ABC<eos>
        batchTrgs = []
        for methodName in methondNameList:
            trgInput, trgLabel = getAllMethodNameSubToken(methodName, methodNameDicPath)
            trgLen = len(trgInput)
            batchTrgs.append((trgInput, trgLabel, trgLen))

        # 返回(midNodeList,leaveList,number of STs,trgInput,trgLabel,trgLen)

        for index in range(batchSize):
            samples.append((batchSTs[index], batchTrgs[index]))

        return samples

    batch, _ = batchSamples(dataPath)
    methodNameList = batch[0]
    rootList = batch[1]
    return generateSample(rootList, methodNameList)
