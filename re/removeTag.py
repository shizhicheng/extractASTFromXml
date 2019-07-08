'''
删除xml多余的标记，方便对xml的一次性解析
'''
import re
import sys
import xml.etree.ElementTree as ET
def parseXML(path):
    try:
        tree = ET.parse(path)

        # 获得根节点
        root = tree.getroot()
        return root
    except Exception as e:  # 捕获除与程序退出sys.exit()相关之外的所有 异常
        print("parse test.xml fail!")
        sys.exit()

if __name__ == "__main__":
    path1 = "I:\\prcessedData\\functionList\\batchXml\\batch7xml.xml"
    path2 = "I:\\prcessedData\\functionList\\batchXml\\batch7temp.xml"
    with open(path1) as f1:
        with open(path2, "w") as f2:

            str = f1.read()
            pattern1 = re.compile(r'<unit .* hash=.{42}>')
            pattern2 = re.compile((r'</unit>'))

            list1 = pattern1.findall(str)
            list2 = pattern2.findall(str)

            removeHeader = re.sub(pattern1, "", str)
            removeTail = re.sub(pattern2, "", removeHeader)

            print("remove length")
            print(len(list1))
            print(len(list2))

            print("**" * 20)
            print("remove header list:")
            for node in list1:
                print(node)

            print("**" * 20)
            print("remove tail list")
            for node in list2:
                print(node)

            f2.write(removeTail)

