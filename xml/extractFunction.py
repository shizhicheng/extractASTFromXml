import json
import sys
import xml.etree.ElementTree as ET
import pickle


# 将所有的函数体存放到同一个文件中
def extractFunction(readFrom, writeTo):
    with open(readFrom, 'r', encoding='utf-8') as f1:
        with open(writeTo, 'a+') as f2:
            for line in f1.readlines():
                str = json.loads(line)
                methodBody = str["methodBody"]
                try:
                    f2.write(methodBody)
                except UnicodeEncodeError:
                    continue


# 解析xml文件
def parseXML(path):
    try:
        tree = ET.parse(path)

        # 获得根节点
        root = tree.getroot()
        return root
    except Exception as e:  # 捕获除与程序退出sys.exit()相关之外的所有 异常
        print("parse test.xml fail!")
        sys.exit()


def extractMethodName(readFrom):
    methodNameList = []
    with open(readFrom) as f:
        for line in f.readlines():
            str = json.loads(line)
            methodNameList.append(str["methodName"])
    return methodNameList


# 将srcml解析后的xml，序列化存储function
def functionXmlToPickle(readFrom, writeTo):
    root = parseXML(readFrom)
    count = 0
    functionList = root.findall("function")
    with open(writeTo, 'ab+') as f:
        for node in functionList:
            functionName = node.find("name")
            tup = (functionName.text, node)
            pickle.dump(tup, f)
            count += 1
            if (count % 1000 == 0):
                print("已经写入：" + str(count))


# 遍历树
def traverse(node):
    print(node.tag)
    for childNode in node:
        traverse(childNode)


# 从序列化的输出文件中读取数据
def readPickle(readFrom):
    with open(readFrom, 'rb') as f:
        data = pickle.load(f)
        while data != None:
            print(data)
            try:
                data = pickle.load(f)
            except EOFError:
                break


#


# 因为将所有的函数都放在同一个文件下srcml解析不了，所以分成多个文件存放函数放在一个文件夹下面
def splitFunctions(readFrom, writeToDir, num):
    # 统计读入的函数的数目
    count = 0
    # 每个文件存储num个函数体，当一个文件存满了之后，函数名加一
    fileName = 1

    with open(readFrom, "r", encoding='utf-8') as f1:
        with open(writeToDir + "\\" + str(fileName) + ".java", "a+") as f2:
            for line in f1.readlines():
                count += 1

                # 判断文件是否写满了指定数目的函数
                if count % num == 0:
                    fileName += 1
                    f2.close()
                    f2 = open(writeToDir + "\\" + str(fileName) + ".java", "a+")

                # 将函数体写出
                jsonString = json.loads(line)
                functionBody = jsonString["methodBody"]
                try:
                    f2.write(functionBody)
                except UnicodeEncodeError:
                    continue

        f2.close()


def preprocessXml(XmlDir, num, writeTo):
    for i in range(num):
        readFrom = XmlDir + "\\batch" + str(i + 1)
        functionXmlToPickle(readFrom, writeTo)


def countMethodNum(readFrom):
    count = 1

    with open(readFrom, 'rb') as f:
        data = pickle.load(f)
        while data != None:
            count += 1
            if count % 10000 == 0:
                print(count)
            try:
                data = pickle.load(f)
            except EOFError:
                break

    print("the total number of method:" + str(count))


if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
    path7 = "I:\\prcessedData\\functionList\\batchXml\\batch7temp.xml"
    path8 = "I:\\prcessedData\\functionList\\batchXml\\batch.data"
    # functionXmlToPickle(path7, path8)
    # readPickle(path8)
    countMethodNum(path8)
