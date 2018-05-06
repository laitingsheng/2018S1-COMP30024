import numpy as np
import json

try:
    from keras.layers import Dense
    from keras.models import load_model, model_from_json, Sequential
    from keras.utils import multi_gpu_model

    class PlaceNNet:
        def __init__(self, load=False):
            if load:
                self._model = load_model("./temp/place_curr.h5")
            else:
                self._model = Sequential([
                    Dense(128, input_dim=64, activation="relu"),
                    Dense(128, activation="relu"),
                    Dense(128, activation="relu"),
                    Dense(128, activation="relu"),
                    Dense(128, activation="relu"),
                    Dense(48, activation="tanh")
                ])

            self.model = multi_gpu_model(self._model)
            self.model.compile(loss="mse", optimizer="adam")

    class MoveNNet:
        def __init__(self, load=False):
            if load:
                self._model = load_model("./temp/move_curr.h5")
            else:
                self._model = Sequential([
                    Dense(1024, input_dim=64, activation="relu"),
                    Dense(1024, activation="relu"),
                    Dense(1024, activation="relu"),
                    Dense(1024, activation="relu"),
                    Dense(1024, activation="relu"),
                    Dense(512, activation="tanh")
                ])

            self.model = multi_gpu_model(self._model)
            self.model.compile(loss="mse", optimizer="adam")
except ModuleNotFoundError:
    from Pretrained import PlaceNNet, MoveNNet


class Evaluation:
    def __init__(self, load=False):
        self.place = PlaceNNet(load)
        self.move = MoveNNet(load)

    def predict(self, board):
        if board.placing:
            return self.place.model.predict(board.canonical)
        return self.move.model.predict(board.canonical)

    def save(self, key, suffix):
        self.place._model.save(f"./temp/place_{suffix}.h5")
        self.move._model.save(f"./temp/move_{suffix}.h5")

    def train(self, board, vv):
        if board.placing:
            self.place.model.fit(board.canonical, vv)
        else:
            self.move.model.fit(board.canonical, vv)
