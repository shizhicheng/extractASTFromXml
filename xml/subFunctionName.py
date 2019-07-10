
import pickle
import xml.etree.ElementTree as ET
import sys
'''
将所有的函数名替换为f
'''

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


# 将所有函数名替换为f
def subFunctionName(readFrom, writeTo):
    count = 1
    with open(readFrom, 'rb') as f1:
        with open(writeTo, "ab+")as f2:
            data = pickle.load(f1)
            while data != None:

                # 每处理10000个data，打印一下
                if count % 10000 == 0:
                    print(count)
                count += 1

                # 将函数名全部修改为f
                element = data[1]
                functionNameElement = element.find("name")
                functionNameElement.text = "f"

                # 将修改后的对象写出
                pickle.dump(data, f2)

                try:
                    data = pickle.load(f1)
                except EOFError:
                    break


# 测试函数名有没有修改成功
def testFunctionNameModify(readFrom):
    with open(readFrom, 'rb') as f:
        data = pickle.load(f)
        data2 = pickle.load(f)
        data3 = pickle.load(f)
        root = data3[1]
        functionNameElement = root.find("name")
        print(functionNameElement.text)


if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
    readFrom = "I:\\prcessedData\\functionList\\batchXml\\batch.data"
    writeTo = "I:\\prcessedData\\functionList\\batchXml\\batchReplaceFunctionName.data"
    # subFunctionName(readFrom,writeTo )
    # testFunctionNameModify(writeTo)
