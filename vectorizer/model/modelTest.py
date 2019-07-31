from vectorizer.model.config import *
import time
import tensorflow as tf
# from vectorizer.model.sampling import makeDataSet, padListsToMatrix, removeLeaveNodePadEmbeddings, \
#     removeMidNodePadEmbeddings
from vectorizer.model.constVariable import *
from vectorizer.model.samplingTest import *
from vectorizer.parameters import NUM_FEATURES  # 中间节点向量的维度
import pickle


class ASTNN:
    def __init__(self):
        # 定义编码器所使用的的神经元
        self.encode_cell_fw = tf.nn.rnn_cell.BasicLSTMCell(HIDDEN_SIZE)
        self.encode_cell_bw = tf.nn.rnn_cell.BasicLSTMCell(HIDDEN_SIZE)

        # 定义解码器所使用的LSTM结构
        self.dec_cell = tf.nn.rnn_cell.MultiRNNCell(
            [
                tf.nn.rnn_cell.BasicLSTMCell(HIDDEN_SIZE)
                for _ in range(NUM_LAYER)
            ]
        )

        # 为中间节点，叶子节点，函数名节点分别定义词向量
        self.leaveEmbedding = tf.get_variable(
            "leave", [LEAVE_VOCAB_SIZE, HIDDEN_SIZE]
        )
        self.targetEmbedding = tf.get_variable(
            "target", [TAR_VOCAB_SIZE, HIDDEN_SIZE]
        )

        # 中间节点向量矩阵通过Word2vect预训练得到，直接从外存读入
        with open(midNodeEmbeddingPath, "rb") as f:
            embeddingAndDicTuple = pickle.load(f)
            self.midNodeEmbedding = embeddingAndDicTuple[0]

        # 定义处理合并向量的矩阵以及bias
        self.merge_weight = tf.get_variable(
            "merge_weight", [HIDDEN_SIZE + NUM_FEATURES, HIDDEN_SIZE]
        )
        self.merge_bias = tf.get_variable(
            "merge_bias", [HIDDEN_SIZE]
        )

        # 定义softmax层变量
        if SHARE_EMB_AND_SOFTMAX:
            self.softmax_weight = tf.transpose(self.targetEmbedding)
        else:
            self.softmax_weight = tf.get_variable(
                "weight", [HIDDEN_SIZE, TAR_VOCAB_SIZE]
            )
        self.softmax_bias = tf.get_variable(
            "bias", [TAR_VOCAB_SIZE]
        )

    def forward(self):

        midNodeListPad = tf.placeholder(tf.int32,shape=[BATCH_SIZE,None,None], name="midNodeListPad")
        leaveNodeListPad = tf.placeholder(tf.int32,shape=[BATCH_SIZE,None,None], name="leaveNodeListPad")
        trgInputPad = tf.placeholder(tf.int32,shape=[BATCH_SIZE,None], name="midNodeListPad")
        trgLabelPad = tf.placeholder(tf.int32,shape=[BATCH_SIZE,None], name="midNodeListPad")

        midNodeMaskInput = tf.placeholder(tf.int32,shape=[BATCH_SIZE,None,None], name="midNodeMaskInput")
        leaveNodeMaskInput = tf.placeholder(tf.int32,shape=[BATCH_SIZE,None,None], name="leaveNodeMaskInput")

        STNum = tf.placeholder(tf.int32,shape=[BATCH_SIZE], name="STNum")
        trg_size = tf.placeholder(tf.int32,shape=[BATCH_SIZE], name="trg_size")

        # 获得中间节点向量矩阵 batchSize * statementLen * maxListLen * NUM_FEATURES
        # maxListLen为每个batch中最长list的维度
        midNodeEmbedding = tf.nn.embedding_lookup(self.midNodeEmbedding, midNodeListPad)

        # 获得叶子节点向量矩阵 batchSize * statementLen  *  maxListLen * HIDDEN_SIZE
        leaveEmbedding = tf.nn.embedding_lookup(self.leaveEmbedding, leaveNodeListPad)

        # 获得目标向量的矩阵 batchSize *  statementLen  *  maxListLen * HIDDEN_SIZE
        trgEmbedding = tf.nn.embedding_lookup(self.targetEmbedding, trgInputPad)

        # 将填充的向量设置为零向量

        # 根据midNodeList创建一个矩阵midNodeMask，矩阵的每个维度的大小是列表中的最高维度的大小，
        # 得到的矩阵包含两个值0，以及向量的大小
        # 如果是0，则该位置经过mask变换后将形成一个0向量
        # 若是向量的大小，经过mask变换后将保留原先向量的值

        midNodeMask = tf.sequence_mask(midNodeMaskInput, NUM_FEATURES, dtype=tf.float32)
        leaveNodeMask = tf.sequence_mask(leaveNodeMaskInput, HIDDEN_SIZE, dtype=tf.float32)

        midNodeEmbeddingRemovePad = midNodeEmbedding * midNodeMask
        leaveEmbeddingRemovePad = leaveNodeMask * leaveEmbedding

        # 在词向量上进行dropout
        midNodeEmbedding = tf.nn.dropout(midNodeEmbeddingRemovePad, KEEP_PROB)
        leaveEmbedding = tf.nn.dropout(leaveEmbeddingRemovePad, KEEP_PROB)

        # 对特征进行累加求和
        midNodeEmbedding = tf.reduce_sum(midNodeEmbedding, axis=2)
        leaveEmbedding = tf.reduce_sum(leaveEmbedding, axis=2)

        # 对midEmbedding以及leaveEmbedding进行拼接 batchSize * STLen * (NUM_FEATURES + HIDDEN_SIZE)
        mergeEmbedding = tf.concat([midNodeEmbedding, leaveEmbedding], 2)

        # 将合并的向量维度转化成HIDDEN_SIZE，
        rnnEmbedding = tf.tanh(tf.matmul(mergeEmbedding, self.merge_weight) + self.merge_bias)

        # 构造双向循环神经网络编码器
        # 这里的time step就是statement子树的个数
        with tf.variable_scope("encoder"):
            enc_outputs, enc_states = tf.nn.bidirectional_dynamic_rnn(
                self.encode_cell_fw, self.encode_cell_bw, rnnEmbedding, STNum, dtype=tf.float32
            )

        # 将两个LSTM的输出拼接为一个张量
        enc_outputs = tf.concat([enc_outputs[0], enc_outputs[1]], -1)

        with tf.variable_scope("decoder"):
            attention_mechanism = tf.contrib.seq2seq.BahdanauAttention(
                HIDDEN_SIZE, enc_outputs, memory_sequence_length=STNum
            )

            # 将解码器的循环神经网络self.dec_cell和注意力一起封装成更高层次的循环神经网络
            attention_cell = tf.contrib.seq2seq.AttentionWrapper(
                self.dec_cell, attention_mechanism, attention_layer_size=HIDDEN_SIZE
            )

            dec_outputs, _ = tf.nn.dynamic_rnn(
                attention_cell, trgEmbedding, trg_size, dtype=tf.float32
            )

        # 计算解码器的log perplexity
        output = tf.reshape(dec_outputs, [-1, HIDDEN_SIZE])
        logits = tf.matmul(output, self.softmax_weight) + self.softmax_bias
        loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
            labels=tf.reshape(trgLabelPad, [-1]), logits=logits)

        # 在计算平均损失时，需要将填充位的权重设置为0，以避免无效位置的预测干扰
        # 模型的训练

        label_weights = tf.sequence_mask(
            trg_size, maxlen=tf.shape(trgLabelPad)[1], dtype=tf.float32
        )
        label_weights = tf.reshape(label_weights, [-1])
        cost = tf.reduce_sum(loss * label_weights)
        cost_per_token = cost / tf.reduce_sum(label_weights)

        # 定义反向传播操作
        trainable_variables = tf.trainable_variables()
        grads = tf.gradients(cost / tf.to_float(BATCH_SIZE), trainable_variables)
        grads, _ = tf.clip_by_global_norm(grads, MAX_GRAD_NORM)

        optimizer = tf.train.AdamOptimizer(learning_rate=LEARNING_RATE)
        train_op = optimizer.apply_gradients(zip(grads, trainable_variables))

        return cost_per_token, train_op, midNodeListPad, leaveNodeListPad, trgInputPad, trgLabelPad, midNodeMaskInput, leaveNodeMaskInput, STNum, trg_size


    def main(self):
        initializer = tf.contrib.layers.variance_scaling_initializer(factor=1.0, mode='FAN_OUT', uniform=True)

        # 定义训练用的循环神经网络模型
        with tf.variable_scope("astnn", reuse=None, initializer=initializer):
            train_model = ASTNN()

        #预先将字典加载入内存
        with open(leaveDicPath, "rb") as f:
            leaveDic = pickle.load(f)
        with open(methodNameDicPath, "rb") as f:
            methodNameDic = pickle.load(f)

        # 定义输入数据，sample操作
        sample_gen = batchSamples(BATCH_SIZE,leaveDic,methodNameDic)

        # 定义前向计算图
        cost_op, train_op, midNodeListPad, leaveNodeListPad, trgInputPad, trgLabelPad, midNodeMaskInput, leaveNodeMaskInput, STNum, trgSize = train_model.forward()

        # 训练模型
        saver = tf.train.Saver()
        step = 1

        with tf.Session()  as sess:
            tf.global_variables_initializer().run()
            lostBatch=0
            for i in range(NUM_EPOCH):
                print("In iteration : %d" % (i + 1))

                start = time.time()
                for batch in sample_gen:
                    midNodeList, _, leaveList, _, STNumBatch, trgInput, trgLabel, trgSizeBatch = batch

                    midNodeListPadBatch, leaveNodeListPadBatch, trgInputPadBatch, trgLabelPadBatch = padListsToMatrix(
                        midNodeList, leaveList, trgInput, trgLabel, STNumBatch)

                    midNodeMaskInputBatch = removeMidNodePadEmbeddingsMaskInput(midNodeList, NUM_FEATURES)
                    try:
                        leaveNodeMaskInputBatch = removeLeaveNodePadEmbeddingsMaskInput(leaveList, HIDDEN_SIZE)
                    except MemoryError:
                        lostBatch=0
                        continue
                    cost,_=sess.run([cost_op, train_op], feed_dict={
                        midNodeListPad: midNodeListPadBatch,
                        leaveNodeListPad:leaveNodeListPadBatch,
                        trgInputPad:trgInputPadBatch,
                        trgLabelPad:trgLabelPadBatch,
                        midNodeMaskInput:midNodeMaskInputBatch,
                        leaveNodeMaskInput:leaveNodeMaskInputBatch,
                        STNum:STNumBatch,
                        trgSize:trgSizeBatch
                    })
                    if step % 10 == 0:
                        end=time.time()
                        print("After %d steps ,per token cost is  %.3f, consume %.3f seconds" % (step, cost,end-start))

                    # 每1000步保存一个checkpoint
                    if step % 100 == 0:
                        saver.save(sess, CHECKPOINT_PATH, global_step=step)

                    step +=1

            print("the number of lost batch is ",lostBatch)



if __name__ == "__main__":
    astnn = ASTNN()
    astnn.main()
