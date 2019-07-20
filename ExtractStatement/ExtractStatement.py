import sys
import xml.etree.ElementTree as ET
import pickle
'''
根据函数体源码生成的xml提取statement子树序列
'''

# 带双亲节点的树节点
class treeNode:
    def __init__(self, parent, ele):
        if parent != None:
            self.parent = parent
            self.ele = ele
        else:
            self.parent = parent
            self.ele = ele


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


#
# #根据层次遍历提取树,应该用深度优先遍历提取
# def createNewTree(root, tree):
#     queue = []
#     queue.append(root)
#     while len(queue) > 0:
#         node = queue.pop(0)
#         for childNode in node:
#             # 将带有双亲标记的节点放入列表中
#             tree.append(treeNode(node, childNode))
#             # 将当前节点的所有孩子节点放入队列
#             queue.append(childNode)


# 深度优先遍历树
def traverse(node):
    print(node.tag)
    for childNode in node:
        traverse(childNode)


# 根据深度优先遍历得到的列表，提取statement子树
def extractStatement(tree):
    statementList = []
    for node in tree:
        if node.ele.tag in statemnentTag:
            statementList.append(node.ele)
            if node.parent != None:
                node.parent.remove(node.ele)
    return statementList


# 深度优先遍历树，树的节点为带双亲节点的结构
def createTreeDeepFirst(root, list, parent):
    list.append(treeNode(parent, root))
    for node in root:
        createTreeDeepFirst(node, list, root)


# 对提取statement的过程实现封装
def process(path):
    root = parseXML(path)
    treeDeepFirstList = []
    createTreeDeepFirst(root, treeDeepFirstList, None)
    statementList = extractStatement(treeDeepFirstList)
    return statementList

#根据根节点提取AST
def extractSTBaseRoot(root):
    treeDeepFirstList = []
    createTreeDeepFirst(root, treeDeepFirstList, None)
    statementList = extractStatement(treeDeepFirstList)
    return statementList


# statement节点
statemnentTag = {"if", "while", "for", "do", "break", "continue", "function", "label", "return", "switch", "case",
                 "default", "assert", "block", "decl_stmt", "expr_stmt", "try", "throw", "throws", "catch", "finally",
                 "synchronized"
                 }

# if __name__ == "__main__":
#     with open("I:\\data\\batchReplaceFunctionName.data", "rb") as f:
#         data = pickle.load(f)
#         root0=data[1]
#         print(extractSTBaseRoot(root0))

