import tensorflow as tf
from vectorizer.nodeMap import nodeMap
import math
from vectorizer.parameters import BATCH_SIZE,NUM_FEATURES,HIDDEN_NODES
def init_net(
        batch_size=BATCH_SIZE, num_feats=NUM_FEATURES, hidden_size=HIDDEN_NODES,
):
    """Construct the network graph."""

    with tf.name_scope('network'):

        with tf.name_scope('inputs'):
            # input node-child pairs
            inputs = tf.placeholder(tf.int32, shape=[batch_size,], name='inputs')
            labels = tf.placeholder(tf.int32, shape=[batch_size,], name='labels')

            # embeddings to learn
            embeddings = tf.Variable(
                tf.random_uniform([len(nodeMap), num_feats]), name='embeddings'
            )

            embed = tf.nn.embedding_lookup(embeddings, inputs)
            onehot_labels = tf.one_hot(labels, len(nodeMap), dtype=tf.float32)

        # weights will have features on the rows and nodes on the columns
        with tf.name_scope('hidden'):
            weights = tf.Variable(
                tf.truncated_normal(
                    [num_feats, hidden_size], stddev=1.0 / math.sqrt(num_feats)
                ),
                name='weights'
            )

            biases = tf.Variable(
                tf.zeros((hidden_size,)),
                name='biases'
            )

            hidden = tf.tanh(tf.matmul(embed, weights) + biases)

        with tf.name_scope('softmax'):
            weights = tf.Variable(
                tf.truncated_normal(
                    [hidden_size, len(nodeMap)],
                    stddev=1.0 / math.sqrt(hidden_size)
                ),
                name='weights'
            )
            biases = tf.Variable(
                tf.zeros((len(nodeMap),), name='biases')
            )

            logits = tf.matmul(hidden, weights) + biases

        with tf.name_scope('error'):
            cross_entropy = tf.nn.softmax_cross_entropy_with_logits(
                labels=onehot_labels, logits=logits, name='cross_entropy'
            )

            loss = tf.reduce_mean(cross_entropy, name='cross_entropy_mean')

    return inputs, labels, embeddings, loss
