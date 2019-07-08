'''
根据data文件，提取词汇表，包括AST中间节点以及叶子节点的词汇表
'''
import pickle
import sys
import xml.etree.ElementTree as ET


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
        set.add(node.tag)
        storeChildNodeSet(node, set)
    return set


# 根据data文件提取中间节点结合，并将集合序列化写入外存
def getMediumNode(readFrom, writeTo):
    count = 0
    with open(readFrom, "rb") as f1:
        with open(writeTo) as f2:
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


# 根据data文件提取叶子节点结合，并将集合序列化写入外存
# def getLeafNode(readFrom,writeTo):

if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
    path1 = "I:\\prcessedData\\functionList\\batchXml\\batchReplaceFunctionName.data"
    path2 = "C:\\Users\\shizhicheng\\Desktop\\test.xml"
    nodeSet = getMediumNode(path1, path2)

    print("**" * 20)
    print("the total number of medium set:")
    print(len(nodeSet))
    print("**" * 20)
    print(nodeSet)
