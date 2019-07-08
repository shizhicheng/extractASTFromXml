'''
根据data文件，提取词汇表，包括AST中间节点以及叶子节点的词汇表
'''
import pickle
import sys
import xml.etree.ElementTree as ET
import re


# 解析xml
def parseXML(path):
    try:
        tree = ET.parse(path)

        # 获得根节点
        root = tree.getroot()
        return root
    except Exception as e:  # 捕获除与程序退出sys.exit()相关之外的所有 异常
        print("parse test.xml fail!")
        sys.exit()


# 存储以root为根节点的所有中间节点
def storeChildNodeSet(root, set):
    set.add(root.tag)
    for node in root:
        # set.add(node.tag)
        storeChildNodeSet(node, set)
    return set


# 将以root为根节点的所有叶子节点存储进一个列表
def storeLeaves(root, leafSet):
    if root.text != None:
        leafSet.add(root.text)
    for node in root:
        storeLeaves(node, leafSet)
    return leafSet


# 根据data文件提取中间节点结合
def getMediumNode(readFrom):
    count = 0
    with open(readFrom, "rb") as f1:
        nodeSet = set()
        data = pickle.load(f1)
        while data != None:

            count += 1
            storeChildNodeSet(data[1], nodeSet)
            try:
                data = pickle.load(f1)
            except EOFError:
                break
            if count % 10000 == 0:
                print(count)

        return nodeSet


# 根据data文件提取叶子节点集合
def getLeaves(readFrom):
    count = 0
    with open(readFrom, "rb") as f1:
        leaveSet = set()
        data = pickle.load(f1)
        while data != None:

            count += 1
            storeLeaves(data[1], leaveSet)
            try:
                data = pickle.load(f1)
            except EOFError:
                break

            # 打印已经处理完的数据
            if count % 10000 == 0:
                print(count)

            # # 小规模测试
            # if count == 10000:
            #     break

        return leaveSet


# 过滤掉叶子节点中非字母的信息，并进行分词
def getSubTokens(leaveSet):
    leaveListTemp = list(leaveSet)
    leaveList = []
    for node in leaveListTemp:
        # 若该节点只是由字母组成的
        if node.isalpha():
            # 将该节点根据分词
            pattern = re.compile(r'[A-Z][A-Z]+|[0-9]*[a-z]+[0-9]*|[A-Z]{1}[0-9]*[a-z]*[0-9]*')
            subTokens = pattern.findall(node)
            for subToken in subTokens:
                leaveList.append(subToken.lower())
    return leaveList


# 将词汇表存入字典,并将该字典序列化写入外存
def storeVocabulary(words, writeTo):
    dictionary = dict()
    for word in words:
        dictionary[word] = len(dictionary)
    with open(writeTo,"wb") as f:
        pickle.dump(dictionary, f)


# 统计中间节点以及叶子节点词汇表的信息
def statistic(readFrom, writeTo):
    nodeSet = getMediumNode(readFrom)
    print("**" * 20)
    print("the total number of medium set:")
    print(len(nodeSet))
    print("**" * 20)
    print(nodeSet)

#对获取词汇表的过程进行封装
def storeVocabularyProcess(readFrom, writeTo):
    leaveSet = getLeaves(readFrom)
    leaves = getSubTokens(leaveSet)
    storeVocabulary(leaves, writeTo)
    print("dictionary len:"+str(len(leaves)))


if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
    path1 = "I:\\prcessedData\\functionList\\batchXml\\batchReplaceFunctionName.data"
    path2 = "I:\\prcessedData\\dictionary.data"
    # leaveSet = getLeaves(path1)
    # leaveList = getSubTokens(leaveSet)
    # print(len(leaveList))
    # for node in leaveList:
    #     print(node)
    storeVocabularyProcess(path1,path2)

