import numpy as np
import tensorflow as tf
from vectorizer.model.samplingTest import *


def removeMidNodePadEmbeddings(midNodeList, embeddingSize):
    # 获得这个三维列表的最高维度
    batchSize = len(midNodeList)
    maxDim2 = 0
    maxDim3 = 0
    for index1 in range(0, batchSize):
        if maxDim2 < len(midNodeList[index1]):
            maxDim2 = len(midNodeList[index1])
        for index2 in range(0, len(midNodeList[index1])):
            if maxDim3 < len(midNodeList[index1][index2]):
                maxDim3 = len(midNodeList[index1][index2])

    array = np.zeros(batchSize * maxDim2 * maxDim3)
    matrix = array.reshape(batchSize, maxDim2, maxDim3)

    for index1 in range(0, batchSize):
        for index2 in range(0, len(midNodeList[index1])):
            # 将非填充的statement矩阵都用向量长度进行填充
            # 将填充的statement矩阵都用0进行填充
            matrix[index1][index2] = embeddingSize
            for index3 in range(len(midNodeList[index1][index2]), maxDim3):
                matrix[index1][index2][index3] = 0

    return matrix


def pad2DList(list, dim1, dim2):
    for row in range(0, dim1):
        if row == len(list):
            list.append([])
        while len(list[row]) < dim2:
            list[row].append(0)
    return list


# 填充3维矩阵，形成dim1 * dim2 * dim3 格式的矩阵
def pad3DList(list, dim1, dim2, dim3):
    for index1 in range(0, dim1):
        if index1 == len(list):
            list.append([])
        list[index1] = pad2DList(list[index1], dim2, dim3)
    return list


if __name__ == "__main__":
    c = np.random.random([10, 5])

    list = [
        [
            [1, 2, 3, 4],
            [1, 2, 3]
        ],
        [
            [1, 2, 3, 4, 5, 5, 6, 7],
            [1]
        ],
        [
            [1],
            [1, 2, 3],
            [1, 2, 3, 4]
        ]
    ]

    vocabulary = np.random.random([10, 7])

    matrix = removeMidNodePadEmbeddings(list, 8)
    paddedMatrix = pad3DList(list, 3, 3, 8)
    paddedMatrix = np.asarray(paddedMatrix)
    paddedMatrix.reshape(3, 3, 8)

    # 填充后的矩阵
    print("填充后的矩阵")
    print(paddedMatrix)

    #词汇表
    print("词汇表")
    print(vocabulary)

    embeddings=tf.nn.embedding_lookup(vocabulary,paddedMatrix)
    mask=tf.sequence_mask(matrix,maxlen=7,dtype=tf.float64)

    shape1=tf.shape(embeddings)
    shape2=tf.shape(mask)
    embeddingsRemovePad =embeddings * mask
    with tf.Session() as sess:
        # sess.run([embeddings,mask,shape1,shape2])
        # print(tf.shape(embeddings),tf.shape(mask))
        # print(mask.eval())
        # sess.run(embeddingsRemovePad)
        # print(embeddings.eval())
        # print(embeddingsRemovePad.eval())
        sess.run(embeddingsRemovePad)
        print(embeddingsRemovePad.eval())
