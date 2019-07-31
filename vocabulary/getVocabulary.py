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


# 将叶子节点存放在字典中，（key,count）
def leavesDic(root, dic):
    if root.text != None:
        # 如果在字典中，加1 否则等于0
        # 将该节点根据分词并进行词形还原
        pattern = re.compile(r'[A-Z][A-Z]+|[a-z]+|[A-Z]{1}[a-z]*')
        subTokens = pattern.findall(root.text)

        for token in subTokens:
            token = token.lower()
            if token in dic:
                dic[token] += 1
            else:
                dic.update({token: 1})

    for node in root:
        leavesDic(node, dic)
    return dic


# 对词频最高的num个节点，并进行编号，在这个过程中包含分词的处理
# readFrom 表示存储（methodName，root）的文件路径，root是函数抽象语法树的根节点
def leaveVocabulary(readFrom, num):
    count = 0
    with open(readFrom, "rb") as f1:
        dic = dict()
        data = pickle.load(f1)
        while data != None:

            count += 1
            leavesDic(data[1], dic)
            try:
                data = pickle.load(f1)
            except EOFError:
                break

            # 打印已经处理完的数据
            if count % 10000 == 0:
                print("已经处理完" + str(count))

            # # 小规模测试
            # if count == 10000:
            #     break

        # 根据词频进行排序,选择排名靠前的num个单词
        list = sorted(dic.items(), key=lambda x: x[1])
        list = list[:num] if num > len(list) else list

        print(len(dic))
        print("最后一个单词的词频是：" + str(list[len(list) - 1]))

        # 获取前num个叶子节点的集合
        leavesSet = set()
        for item in list:
            leavesSet.add(item[0])

        # print(leaveSet)

        return leavesSet


# 获取方法名的词汇表
def methodNameVocabulary(readFrom):
    count = 0
    with open(readFrom, "rb") as f1:
        dic = dict()
        data = pickle.load(f1)
        while data != None:

            count += 1
            methodName = data[0]
            pattern = re.compile(r'[A-Z][A-Z]+|[a-z]+|[A-Z]{1}[a-z]*')
            subTokens = pattern.findall(methodName)
            for token in subTokens:
                token = token.lower()
                if token in dic:
                    dic[token] += 1
                else:
                    dic.update({token: 1})
            try:
                data = pickle.load(f1)
            except EOFError:
                break

            # 打印已经处理完的数据
            if count % 10000 == 0:
                print("已经处理完了" + str(count))

            # # 小规模测试
            # if count == 10000:
            #     break

        # 根据词频进行排序
        list = sorted(dic.items(), key=lambda x: x[1])

        print("方法名词汇表：" + str(len(list)))
        # 获取前num个叶子节点的集合
        methodNameSet = set()
        for item in list:
            methodNameSet.add(item[0])

        return methodNameSet


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
            pattern = re.compile(r'[A-Z][A-Z]+|[a-z]+|[A-Z]{1}[a-z]*')
            subTokens = pattern.findall(node)
            for subToken in subTokens:
                leaveList.append(subToken.lower())
    return leaveList


# 将词汇表存入字典,并将该字典序列化写入外存
def storeVocabulary(words, writeTo):
    dictionary = dict()
    for word in words:
        dictionary[word] = len(dictionary)
    with open(writeTo, "wb") as f:
        pickle.dump(dictionary, f)


# 统计中间节点以及叶子节点词汇表的信息
def statistic(readFrom, writeTo):
    nodeSet = getMediumNode(readFrom)
    print("**" * 20)
    print("the total number of medium set:")
    print(len(nodeSet))
    print("**" * 20)
    print(nodeSet)


# 对获取词汇表的过程进行封装
def storeVocabularyProcess(readFrom, writeTo):
    leaveSet = getLeaves(readFrom)
    leaves = getSubTokens(leaveSet)
    storeVocabulary(leaves, writeTo)
    print("dictionary len:" + str(len(leaves)))


#
if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
    path1 = "I:\\data\\batchReplaceFunctionName.data"
    path2 = "..\\data\\dictionary\\leaveDic.data"
    path3 = "..\\data\\dictionary\\methodNameDic.data"

    # unk = 1  # 未知字符
    # sos = 2  # 句子开始字符
    # eos = 3  # 句子终结字符
    #
    # # 生成叶子节点的字典表
    # leaveSet = leaveVocabulary(path1, 120000)
    # with open(path2, "wb") as f:
    #     if "unk" in leaveSet:
    #         leaveSet.remove("unk")
    #     leaveList = list(leaveSet)
    #
    #
    #     leaveList.insert(0, "unk")
    #     nodeMap = {x: i + 1 for (i, x) in enumerate(leaveList)}
    #     print(nodeMap)
    #     pickle.dump(nodeMap, f)

    # # 生成方法名的字典表
    # methodNameSet = methodNameVocabulary(path1)
    # with open(path3, "wb") as f:
    #     # 如果原先的集合包含这三个字段则删除
    #     if "unk" in methodNameSet:
    #       methodNameSet.remove("unk")
    #     if "sos" in methodNameSet:
    #         methodNameSet.remove("sos")
    #     if "eos" in methodNameSet:
    #         methodNameSet.remove("eos")

        # # 将集合转变成列表，在列表的开头插入这三个字段，再将列表转化成字典
        # methodNameList = list(methodNameSet)
        # methodNameList.insert(0, 'unk')
        # methodNameList.insert(0, 'sos')
        # methodNameList.insert(0, "eos")
        #
        # nodeMap = {x: i + 1 for (i, x) in enumerate(methodNameList)}
        # print(nodeMap)
        # pickle.dump(nodeMap, f)

    with open(path3,"rb") as f:
        dic=pickle.load(f)
        print(dic["eos"])

