from vectorizer.model.config import LSTM_UNIT, HIDDEN_SIZE, NUM_LAYER, LEAVE_VOCAB_SIZE, MIDDLE_NODE_VOCAB_SIZE, \
    TAR_VOCAB_SIZE, SHARE_EMB_AND_SOFTMAX, KEEP_PROB
import tensorflow as tf
from vectorizer.model.sampling import makeDataSet
from vectorizer.model.constVariable import leaveDicPath, methodNameDicPath, midNodeEmbeddingPath
import pickle


class model:
    def __init__(self):
        # 定义编码器和解码器所使用的的神经元
        # 使用LSTM神经元结构或者GRU结构
        cell = tf.nn.rnn_cell.BasicLSTMCell(HIDDEN_SIZE) if LSTM_UNIT else tf.contrib.rnn.GRUCell(HIDDEN_SIZE)

        # 定义编码器和解码器使用的结构
        self.encodeCell = tf.nn.rnn_cell.MultiRNNCell(
            [
                cell for _ in range(NUM_LAYER)
            ]
        )
        self.decodeCell = tf.nn.rnn_cell.MultiRNNCell(
            [
                cell for _ in range(NUM_LAYER)
            ]
        )

        # 为中间节点，叶子节点，函数名节点分别定义词向量
        self.leaveEmbedding = tf.get_variable(
            "leave", [LEAVE_VOCAB_SIZE, HIDDEN_SIZE]
        )
        self.targetEmbedding = tf.get_variable(
            "target", [TAR_VOCAB_SIZE, HIDDEN_SIZE]
        )

        # 中间节点向量举证通过Word2vect预训练得到，直接从外存读入
        with open(midNodeEmbeddingPath, "rb") as f:
            embeddingAndDicTuple = pickle.load(f)
            self.midNodeEmbedding = embeddingAndDicTuple[0]

        # 定义softmax层变量
        if SHARE_EMB_AND_SOFTMAX:
            self.softmax_weight = tf.transpose(self.targetEmbedding)
        else:
            self.softmax_weight = tf.get_variable(
                "weight", [HIDDEN_SIZE, TAR_VOCAB_SIZE]
            )
        self.softmaxBias = tf.get_variable(
            "bias", [TAR_VOCAB_SIZE]
        )

    def forward(self, midNodeList, leaveList, STLen, trgInput, trgLabel, trgLen):

        # 获得中间节点向量矩阵
        midEmbedding = tf.nn.embedding_lookup(self.midNodeEmbedding, midNodeList)

        # 获得叶子节点向量矩阵
        leaveEmbedding = tf.nn.embedding_lookup(self.leaveEmbedding, leaveList)

        # 获得目标向量的矩阵
        trgEmbedding = tf.nn.embedding_lookup(self.targetEmbedding, trgInput)

        #在词向量上进行dropout
        midEmbedding = tf.nn.dropout(midEmbedding, KEEP_PROB)
        leaveEmbedding = tf.nn.dropout(leaveEmbedding, KEEP_PROB)

        # 将叶子节点向量矩阵进行最大层池化
