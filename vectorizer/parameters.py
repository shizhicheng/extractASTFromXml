'''
存储一些常量
'''

# 替换了函数名的文件路径
dataPath = "I:\\data\\batchReplaceFunctionName.data"
samplePath="I:\\data\\samples.data"
trainPath="I:\\data\\smallDataSet\\train.data"
validataPath="I:\\data\\smallDataSet\\validate.data"
testPath="I:\\data\\smallDataSet\\test.data"

#测试xml路径
testXmlPath="C:\\Users\\shizhicheng\\Desktop\\test.xml"

#hyperParameters
NUM_FEATURES = 30
BATCH_SIZE = 256



EPOCHS = 100

LEARN_RATE = 0.01
HIDDEN_NODES = 100

CHECKPOINT_EVERY = 10000

#保存的文件路径
logdir="C:\\Users\shizhicheng\\PycharmProjects\\extractASTFromXml\\log"
outfile="C:\\Users\shizhicheng\\PycharmProjects\\extractASTFromXml\\log\\embeddingFile.data"