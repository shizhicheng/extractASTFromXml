# import xml.etree.ElementTree as ET
# import sys
# import copy
#
# statemnentTag = {"if", "while", "for", "do", "break", "continue", "label", "return", "switch", "case", "default",
#                  "assert", "block",
#                  "decl_stmt", "expr_stmt", "try", "throw", "throws", "catch", "finally"}
#
#
# # 提取root以及其所有子节点的tag
# # def extractTagIntoSet(root):
# #     tagSet = set()
# #     tagSet.add(root.tag)
# #     for node in root:
# #         tagSet.add(node.tag)
# #     return tagSet
#
# def extractTagIntoSet(node, tagSet):
#     tagSet.add(node.tag)
#     nodeList = list(node)
#     if (len(nodeList) != 0):
#         for childNode in nodeList:
#             extractTagIntoSet(childNode, tagSet)
#     return tagSet
#
#
# # 解析以path为路径的xml文件
# def parseXML(path):
#     try:
#         tree = ET.parse(path)
#
#         # 获得根节点
#         root = tree.getroot()
#         return root
#     except Exception as e:  # 捕获除与程序退出sys.exit()相关之外的所有 异常
#         print("parse test.xml fail!")
#         sys.exit()
#
#
# # 删除列表中最后一个匹配
# def removeListLastMatch(list, obj):
#     list.reverse()
#     list.remove(obj)
#     list.reverse()
#     return list
#
#
# # 提取以root为根节点的statement子树序列
# # def extractStatement(root, stmtTree, parentStack):
# #     root.insert(0, root)
# #     rootSize = len(root)
# #
# #     for index in range(len(root)):
# #         tagSet = extractTagIntoSet(root[index])
# #
# #         # 如果当前节点是stmt节点，且孩子节点中存在stmt节点，则将当前节点压入栈中
# #         # print(root[index].tag)
# #         if len(tagSet.intersection(statemnentTag)) > 1 and root[index].tag in tagSet:
# #             parentStack.append(root[index])
# #
# #             extractStatement(root[index + 1], stmtTree, parentStack)
# #             return
# #
# #         # 如果当前节点不是stmt节点，且孩子节点中存在stmt节点，则继续向下寻找stmt接地那
# #         elif len(tagSet.intersection(statemnentTag)) >= 1 and root[index].tag not in tagSet:
# #             extractStatement(root[index + 1], stmtTree, parentStack)
# #             return
# #
# #         # 如果当前节点是stmt节点，且孩子节点中不存在stmt节点，则将当将当前节点存储到stmtTree列表中,并在树中删除当前节点
# #         # 且返回到上一个父亲节点stmt节点中
# #         elif len(tagSet.intersection(statemnentTag)) == 1 and root[index].tag in tagSet:
# #             stmtTree.append(root[index])
# #
# #             # 如果双亲栈不为空
# #             if (len(parentStack) != 0):
# #                 lastParent = parentStack.pop(-1)
# #                 # 在双亲节点中删除当前节点
# #                 lastParent.remove(root[index])
# #                 # 在双亲孩子节点列表中删除自身，因为在初始化的时候会再次添加自身
# #                 del lastParent[0]
# #                 extractStatement(lastParent, stmtTree, parentStack)
# #             else:
# #                 return
# #
# #         # 如果当前节点不是stmt节点，且孩子节点中不存在stmt节点，则返回到上一个父亲节点stmt节点中
# #         elif len(tagSet.intersection(statemnentTag)) < 1 and root[index].tag not in tagSet:
# #
# #             # 如果双亲栈不为空
# #             if (len(parentStack) != 0):
# #                 lastParentIndex = parentStack.pop(-1)
# #                 extractStatement(root[lastParentIndex], stmtTree, lastParentIndex)
# #             else:
# #                 return
#
# def extractStatement(root, stmtTree, parentStack):
#     for index in range(len(root)):
#
#         # 如果当前节点是stmt节点，且孩子节点中存在stmt节点，则将当前节点压入栈中
#         if index == 0:
#             current = root
#         else:
#             current = root[index - 1]
#
#         tagSet = set()
#         tagSet = extractTagIntoSet(current, tagSet)
#
#         if len(tagSet.intersection(statemnentTag)) > 1 and current.tag in tagSet:
#             parentStack.append(current)
#
#             extractStatement(root[index + 1], stmtTree, parentStack)
#             return
#
#         # 如果当前节点不是stmt节点，且孩子节点中存在stmt节点，则继续向下寻找stm t接地那
#         elif len(tagSet.intersection(statemnentTag)) >= 1 and current.tag not in tagSet:
#             extractStatement(root[index + 1], stmtTree, parentStack)
#             return
#
#         # 如果当前节点是stmt节点，且所有孩子节点中不存在stmt节点，则将当前节点存储到stmtTree列表中,并在树中删除当前节点
#         # 且返回到上一个父亲节点stmt节点中
#         elif len(tagSet.intersection(statemnentTag)) == 1 and current.tag in tagSet:
#             stmtTree.append(current)
#
#             # 如果双亲栈不为空
#             if (len(parentStack) != 0):
#                 lastParent = parentStack.pop(-1)
#                 # 在双亲节点中删除当前节点
#                 lastParent.remove(current)
#                 # 在双亲孩子节点列表中删除自身，因为在初始化的时候会再次添加自身
#                 extractStatement(lastParent, stmtTree, parentStack)
#             else:
#                 return
#
#         # 如果当前节点不是stmt节点，且孩子节点中不存在stmt节点，则返回到上一个父亲节点stmt节点中
#         elif len(tagSet.intersection(statemnentTag)) < 1 and current.tag not in tagSet:
#
#             # 如果双亲栈不为空
#             if (len(parentStack) != 0):
#                 lastParentIndex = parentStack.pop(-1)
#                 extractStatement(root[lastParentIndex], stmtTree, lastParentIndex)
#             else:
#                 return
#
#
# def traverse(node):
#     print(node)
#     nodeList = list(node)
#     if (len(nodeList) != 0):
#         for childNode in nodeList:
#             # print(list(childNode))
#             traverse(childNode)
#
#
# if __name__ == "__main__":
#     path = "C:\\Users\\shizhicheng\\Desktop\\testxml.xml"
#     root = parseXML(path)
#
#     stmtTree = []
#     parentStack = []
#     extractStatement(root, stmtTree, parentStack)
#
#     stmtlist = list(stmtTree[0])
#     stmtlist.pop(0)
#     del stmtTree[0][0]
#     # print(stmtTree)
#     traverse(stmtTree[0])
#
# #     stmtlist=[]
# # #去除每个statement根节点的第一个孩子节点
# #     for index1 in range(len(stmtTree)):
# #         for index2 in range(len(stmtTree[index1])):
# #             # stmtTree[index1].pop(0)
# #             print()
