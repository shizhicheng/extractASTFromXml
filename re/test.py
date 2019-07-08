import re

if __name__ == "__main__":
    str = "helloWorldTestSex"
    pattern = re.compile(r'[A-Z][A-Z]+|[0-9]*[a-z]+[0-9]*|[A-Z]{1}[0-9]*[a-z]*[0-9]*')

    list = pattern.findall(str)
    print(list)
