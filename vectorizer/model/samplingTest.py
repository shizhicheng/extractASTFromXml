from vectorizer.model.config import BATCH_SIZE
from ExtractStatement.ExtractStatement import *
import pickle
from vectorizer.nodeMap import nodeMap
import re
import copy
import numpy as np
from vectorizer.model.constVariable import *

isExcute = False  # 用来第一次移动文件指针


# 获得批处理数据,方法名和方法体
def batchSamples(batchSize, leaveDic, methodNameDic):
    with open(dataPath, "rb") as f:
        ###将文件指针移动到断点位置
        count = 1
        global isExcute

        if isExcute is False:
            while count <= 122000:
                pickle.load(f)
                count += 1
            print("read from %d data" % (count-1))
        isExcute = True
        ###

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
            if count >= batchSize:
                rootList = batch[1]
                methondNameList = batch[0]

                midNodesList, midNodesListLen, leaveNodesList, leaveNodesListLen, STNum, trgInput, trgLabel, trgLen = \
                    generateBatchSample(rootList, methondNameList, leaveDic, methodNameDic)
                yield midNodesList, midNodesListLen, leaveNodesList, leaveNodesListLen, STNum, trgInput, trgLabel, trgLen
                batch, count = ([], []), 0


# 获得所有叶子节点
# root:根节点
# path:叶子节点的字典
def getAllLeave(root, leaveDic, leaveList):
    # leaveList = []
    if root.text != None:
        # 对叶子节点进行分词，词性还原(默认将大写还原成小写)
        rootText = root.text
        # 分词
        pattern = re.compile(r'[A-Z][A-Z]+|[a-z]+|[A-Z]{1}[a-z]*')
        subTokens = pattern.findall(rootText)

        # 提取词干并转化成该词的编号
        for token in subTokens:
            token = token.lower()
            if token in leaveDic:
                leaveList.append(leaveDic[token])
            else:
                leaveList.append(leaveDic[UNK_ID])

    for node in root:
        getAllLeave(node, leaveDic, leaveList)

    return leaveList


# 获得所有中间节点
def getAllMidNode(root, midNodeList):
    # midNodeList = []
    midNodeList.append(nodeMap[root.tag])
    for node in root:
        getAllMidNode(node, midNodeList)
    return midNodeList


# 获得方法名的subtoken序列
def getAllMethodNameSubToken(methodName, methodNameDic):
    # 分词
    pattern = re.compile(r'[A-Z][A-Z]+|[a-z]+|[A-Z]{1}[a-z]*')
    subTokens = pattern.findall(methodName)

    # 提取词干并转化成该词的编号
    methodNameList = []
    for token in subTokens:
        token = token.lower()
        if token in methodNameDic:
            methodNameList.append(methodNameDic[token])
        else:
            methodNameList.append(methodNameDic[UNK_ID])

    # 获得trgInput,trgLabel
    trgInput = copy.deepcopy(methodNameList)
    trgInput.insert(0, methodNameDic[SOS_ID])

    trgLabel = methodNameList.copy()
    trgLabel.append(methodNameDic[EOS_ID])

    return trgInput, trgLabel


def generateBatchSample(rootList, methondNameList, leaveDic, methodNameDic):
    midNodesList = []
    midNodesListLen = []
    leaveNodesList = []
    leaveNodesListLen = []
    STNum = []
    trgInput = []
    trgLabel = []
    trgLen = []

    for root in rootList:
        # 将单个语法树切分成多个statement子树
        STs = extractSTBaseRoot(root)

        # 获得该树statement子树的数目
        STNum.append(len(STs))

        # 存放单棵AST所有statement信息
        statemenntTreeMidNodesList = []  # [ [] ]
        statementTreeMidNodesListLen = []  # []

        statementTreeLeaveList = []  # [ [] ]
        statementTreeLeaveListLen = []  # []
        for node in STs:
            # 获得子树中间节点编号,以及该子树中间节点的数目
            singleStatementTreeMidNodesList = getAllMidNode(node, [])  # []
            statemenntTreeMidNodesList.append(singleStatementTreeMidNodesList)  # [ [] ]
            statementTreeMidNodesListLen.append(len(singleStatementTreeMidNodesList))  # [ ]

            # 获得子树叶子节点编号，以及该子树叶子节点的数目
            singleStatementTreeLeaveList = getAllLeave(node, leaveDic, [])  # []
            statementTreeLeaveList.append(singleStatementTreeLeaveList)  # [ [] ]
            statementTreeLeaveListLen.append(len(singleStatementTreeLeaveList))  # [ ]

        # 添加单棵AST的statement信息
        midNodesList.append(statemenntTreeMidNodesList.copy())
        midNodesListLen.append(statementTreeMidNodesListLen.copy())

        leaveNodesList.append(statementTreeLeaveList.copy())
        leaveNodesListLen.append(statementTreeLeaveListLen.copy())

        # 清空列表，下次循环重新填入statement子树信息
        statemenntTreeMidNodesList.clear()
        statementTreeMidNodesListLen.clear()
        statementTreeLeaveList.clear()
        statementTreeLeaveListLen.clear()

    # 对方法进行处理，若方法名分词得到ABC，则处理得到两种形式的数据表示：
    # <sos>ABC  ABC<eos>
    for methodName in methondNameList:
        singleTrgInput, singleTrgLabel = getAllMethodNameSubToken(methodName, methodNameDic)
        singleTrgLen = len(singleTrgInput)
        trgInput.append(singleTrgInput.copy())
        trgLabel.append(singleTrgLabel.copy())
        trgLen.append(singleTrgLen)

    return midNodesList, midNodesListLen, leaveNodesList, leaveNodesListLen, STNum, trgInput, trgLabel, trgLen


# 填充成规范化的矩阵
def padListsToMatrix(midNodesList, leaveNodesList, trgInput, trgLabel, STNum):
    # 填充二维列表，形成dim1 * dim2 格式的矩阵
    # dim1,dim2为填充后的维度
    def pad2DList(list, dim1, dim2):
        for row in range(0, dim1):
            if row == len(list):
                list.append([])
            while len(list[row]) < dim2:
                list[row].append(0)
        return list

    # 填充3维矩阵，形成dim1 * dim2 * dim3 格式的矩阵
    def pad3DList(list, dim1, dim2, dim3):
        for index1 in range(0, dim1):
            if index1 == len(list):
                list.append([])
            list[index1] = pad2DList(list[index1], dim2, dim3)
        return list

    # 从3维列表中，取出第二维最大的值
    def getMaxSecondDimFrom3DList(list):
        max = 0
        for index in range(0, len(list)):
            if max < len(list[index]):
                max = len(list[index])
        return max

    # 从3维列表中，取出第三维最大的值
    def getMaxThirdDimFrom3DList(list):
        max = 0
        for index1 in range(0, len(list)):
            for index2 in range(0, len(list[index1])):
                if max < len(list[index1][index2]):
                    max = len(list[index1][index2])
        return max

    # 从2维列表中，取出第二维最大值
    def getSecondDimFrom2DList(list):
        max = 0
        for index in range(0, len(list)):
            if max < len(list[index]):
                max = len(list[index])
        return max

    # 下面对矩阵进行填充，满足tf.nn.embedding_lookup()，对于输入矩阵维度的要求
    # 首先获得每个维度的最大值
    maxStatementTreeNum = max(STNum)
    maxMidNodesNum = getMaxThirdDimFrom3DList(midNodesList)
    maxLeaveNodeLists = getMaxThirdDimFrom3DList(leaveNodesList)
    maxTrgInput = getSecondDimFrom2DList(trgInput)
    maxTrgLabel = getSecondDimFrom2DList(trgLabel)

    # 对列表进行填充，形成规范化的矩阵
    midNodesListPad = pad3DList(midNodesList, BATCH_SIZE, maxStatementTreeNum, maxMidNodesNum)
    leaveNodesListPad = pad3DList(leaveNodesList, BATCH_SIZE, maxStatementTreeNum, maxLeaveNodeLists)
    trgInputPad = pad2DList(trgInput, BATCH_SIZE, maxTrgInput)
    trgLabelPad = pad2DList(trgLabel, BATCH_SIZE, maxTrgLabel)
    return midNodesListPad, leaveNodesListPad, trgInputPad, trgLabelPad


def removeMidNodePadEmbeddingsMaskInput(midNodeList, embeddingSize):
    # 获得这个三维列表的最高维度
    batchSize = len(midNodeList)
    maxDim2 = 0
    maxDim3 = 0
    for index1 in range(0, batchSize):
        if maxDim2 < len(midNodeList[index1]):
            maxDim2 = len(midNodeList[index1])
        for index2 in range(0, len(midNodeList[index1])):
            if maxDim3 < len(midNodeList[index1][index2]):
                maxDim3 = len(midNodeList[index1][index2])

    array = np.zeros(batchSize * maxDim2 * maxDim3)
    matrix = array.reshape(batchSize, maxDim2, maxDim3)

    for index1 in range(0, batchSize):
        for index2 in range(0, len(midNodeList[index1])):
            # 将非填充的statement矩阵都用向量长度进行填充
            # 将填充的statement矩阵都用0进行填充
            matrix[index1][index2] = embeddingSize
            for index3 in range(len(midNodeList[index1][index2]), maxDim3):
                matrix[index1][index2][index3] = 0

    return matrix


# 因为操作和中间节点相同，所以这里直接调用处理中间节点的函数
def removeLeaveNodePadEmbeddingsMaskInput(leaveNodeList, embeddingSize):
    return removeMidNodePadEmbeddingsMaskInput(leaveNodeList, embeddingSize)
