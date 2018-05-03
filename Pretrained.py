import numpy as np
from abc import ABCMeta
from scipy.special import expit


class NumpyModel(metaclass=ABCMeta):
    def predict(self, board):
        return np.tanh(np.dot(expit(np.dot(np.maximum(np.dot(
            board, self.l1
        ) + self.b1, 0), self.l2) + self.b2), self.l3) + self.b3)


class PlaceModel(NumpyModel):
    def __init__(self):
        self.l1 = np.load("./pretrained/place_weights_0.npy")
        self.b1 = np.load("./pretrained/place_weights_1.npy")
        self.l2 = np.load("./pretrained/place_weights_2.npy")
        self.b2 = np.load("./pretrained/place_weights_3.npy")
        self.l3 = np.load("./pretrained/place_weights_4.npy")
        self.b3 = np.load("./pretrained/place_weights_5.npy")


class MoveModel(NumpyModel):
    def __init__(self):
        self.l1 = np.load("./pretrained/move_weights_0.npy")
        self.b1 = np.load("./pretrained/move_weights_1.npy")
        self.l2 = np.load("./pretrained/move_weights_2.npy")
        self.b2 = np.load("./pretrained/move_weights_3.npy")
        self.l3 = np.load("./pretrained/move_weights_4.npy")
        self.b3 = np.load("./pretrained/move_weights_5.npy")


class PlaceNNet:
    def __init__(self):
        self.model = PlaceModel()


class MoveNNet:
    def __init__(self):
        self.model = MoveModel()
