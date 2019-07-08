import sys
import xml.etree.ElementTree as ET
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

if __name__=="__main__":
    path1 = "I:\\prcessedData\\functionList\\batchXml\\batch7temp.xml"
    parseXML(path1)