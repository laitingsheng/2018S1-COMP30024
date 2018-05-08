import numpy as np
import json

try:
    from keras.layers import Dense
    from keras.models import load_model, Sequential

    class PlaceNNet:
        def __init__(self, load=False):
            if load:
                self.model = load_model("./temp/place_curr.h5")
            else:
                self.model = Sequential([
                    Dense(128, input_dim=64, activation="relu"),
                    Dense(128),
                    Dense(128),
                    Dense(128),
                    Dense(128),
                    Dense(64, activation="tanh")
                ])
            self.model.compile(loss="mse", optimizer="adam")

    class MoveNNet:
        def __init__(self, load=False):
            if load:
                self.model = load_model("./temp/move_curr.h5")
            else:
                self.model = Sequential([
                    Dense(1024, input_dim=64, activation="relu"),
                    Dense(1024),
                    Dense(1024),
                    Dense(1024),
                    Dense(1024),
                    Dense(512, activation="tanh")
                ])
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

    def save(self, suffix):
        self.place.model.save_weights(f"./temp/place_weights_{suffix}.h5")
        self.move.model.save_weights(f"./temp/move_weights_{suffix}.h5")

    def train(self, board, vv):
        if board.placing:
            self.place.model.fit(board.canonical, vv)
        else:
            self.move.model.fit(board.canonical, vv)
