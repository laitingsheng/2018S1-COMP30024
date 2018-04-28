import numpy as np
import tensorflow as tf


class Evaluation:
    def eval(self, fv):
        return 0


class TrainEvaluation:
    def __init__(self):
        with tf.variable_scope('TrainEvaluation'):
            self.feature_vector_ = tf.placeholder(tf.float32,
                                                  shape=(None, 259),
                                                  name='feature_vector_')
            with tf.variable_scope('layer_1'):
                W_1 = tf.get_variable(
                    'W_1', shape=(259, 5180),
                    initializer=tf.contrib.layers.xavier_initializer()
                )
                hidden = tf.nn.relu(
                    tf.matmul(self.feature_vector_, W_1), name='hidden'
                )

            with tf.variable_scope('layer_2'):
                W_2 = tf.get_variable(
                    'W_2', shape=(5180, 1),
                    initializer=tf.contrib.layers.xavier_initializer()
                )
                self.value = tf.tanh(tf.matmul(hidden, W_2), name='value')

            self.trainable_variables = tf.get_collection(
                tf.GraphKeys.TRAINABLE_VARIABLES,
                scope=tf.get_variable_scope().name
            )
