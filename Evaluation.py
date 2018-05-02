import numpy as np
import json

try:
    from keras.layers import Dense
    from keras.models import Sequential

    class PlaceNNet:
        def __init__(self):
            self.model = Sequential([
                Dense(256, input_dim=64, activation="relu"),
                Dense(1024, activation="relu"),
                Dense(64, activation="tanh")
            ])
            self.model.compile(loss="mse", optimizer="adam")
            with open("./temp/place_config.json", 'w') as f:
                json.dump(self.model.to_json(), f)

    class MoveNNet:
        def __init__(self):
            self.model = Sequential([
                Dense(512, input_dim=64, activation="relu"),
                Dense(4096, activation="relu"),
                Dense(512, activation="tanh")
            ])
            self.model.compile(loss="mse", optimizer="adam")
            with open("./temp/move_config.json", 'w') as f:
                json.dump(self.model.to_json(), f)
except ModuleNotFoundError:
    class PlaceNNet:
        pass

    class MoveNNet:
        pass


class Evaluation:
    def __init__(self):
        self.place = PlaceNNet()
        self.move = MoveNNet()

    def predict(self, board):
        if board.placing:
            return self.place.model.predict(board.canonical)
        return self.move.model.predict(board.canonical)

    def save(self, key, suffix="curr"):
        self.place.model.save_weights(f"./temp/place_weights_{suffix}.h5")
        self.place.model.save_weights(f"./temp/move_weights_{suffix}.h5")

    def train(self, board, vv):
        if board.placing:
            self.place.model.fit(board.canonical, vv)
        else:
            self.move.model.fit(board.canonical, vv)
