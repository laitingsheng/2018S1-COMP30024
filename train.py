import random
import tensorflow as tf

from Player import Player
from Evaluation import TrainEvaluation


class TDSelfPlayer(Player):
    def __init__(self, depth=4, model=TrainEvaluation(), ep=0.2, la=0.7):
        super().__init__(depth=depth, model=model)

        self.opt = tf.train.AdamOptimizer()
        self.grads = tf.gradients(
            self.model.value, self.model.trainable_variables
        )
        self.grads_s = [
            tf.placeholder(tf.float32, shape=tvar.get_shape())
            for tvar in self.model.trainable_variables
        ]
        self.apply_grads = self.opt.apply_gradients(
            zip(self.grads_s, self.model.trainable_variables),
            name='apply_grads'
        )

    def train(self, epsilon):
        pass
