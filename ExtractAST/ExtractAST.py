import os
import sys
import xml.dom.minidom as xmldom
import xml.etree.ElementTree as ET
import copy


# 用来存储树结构的树节点
class node():
    def __init__(self, parent, node, childList):
        self.parent = parent
        self.node = node
        self.childList = childList


# 将xml dom树的元素存储到tree中
def storeElementTree(root, tree):
    elementTreeNode = node(None, root, [])
    tree.append(elementTreeNode)

    # 初始化时，设置parent节点
    subElementTreeNode = node(elementTreeNode, None, [])

    # print(elementTreeNode.node.tag)
    for childNode in root:
        # 设置node节点
        childCopyNode = copy.deepcopy(childNode)
        subElementTreeNode.node = childCopyNode

        temp=copy.deepcopy(subElementTreeNode)

        elementTreeNode.childList.append(temp)
        storeElementTree(childNode, tree)
def parseXML(path):
    try:
        tree = ET.parse(path)

        # 获得根节点
        root = tree.getroot()
        return root
    except Exception as e:  # 捕获除与程序退出sys.exit()相关之外的所有 异常
        print("parse test.xml fail!")
        sys.exit()

def traverse(node):
    print(node)
    nodeList=list(node)
    if (len(nodeList) != 0):
        for childNode in nodeList:
            traverse(childNode)

if __name__ == "__main__":
    path = "C:\\Users\\shizhicheng\\Desktop\\testxml.xml"
    xmlFilePath = os.path.abspath(path)
    print(xmlFilePath)
    root=parseXML(path)

    tree = []
    storeElementTree(root, tree)
    for node1 in tree:
        print("parent Node:"+str(node1.node.tag))
        for node2 in node1.childList:
            print(node2.node.tag)
        print("\n")