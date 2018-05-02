import numpy as np
import json

try:
    from keras.layers import Dense
    from keras.models import Sequential

    class PlaceNNet:
        def __init__(self):
            self.model = Sequential([
                Dense(256, input_dim=64, activation="relu"),
                Dense(256, activation="relu"),
                Dense(256, activation="relu"),
                Dense(256, activation="relu"),
                Dense(256, activation="relu"),
                Dense(64, activation="tanh")
            ])
            self.model.compile(loss="mse", optimizer="adam")

    class MoveNNet:
        def __init__(self):
            self.model = Sequential([
                Dense(512, input_dim=64, activation="relu"),
                Dense(512, activation="relu"),
                Dense(512, activation="relu"),
                Dense(512, activation="relu"),
                Dense(512, activation="relu"),
                Dense(512, activation="relu"),
                Dense(512, activation="relu"),
                Dense(512, activation="relu"),
                Dense(512, activation="relu"),
                Dense(512, activation="tanh")
            ])
            self.model.compile(loss="mse", optimizer="adam")
except ModuleNotFoundError:
    class PlaceNNet:
        pass

    class MoveNNet:
        pass


class Evaluation:
    def __init__(self):
        self.place = PlaceNNet()
        self.move = MoveNNet()

    def eval(self, board):
        if board.placing:
            return np.argmax(self.place.model.predict(board.canonical))
        return np.argmax(self.move.model.predict(board.canonical))

    def predict(self, board):
        if board.placing:
            return self.place.model.predict(board.canonical)
        return self.move.model.predict(board.canonical)

    def save(self, key):
        with open(f"./temp/place_config_{key}.json", 'w') as f:
            json.dump(self.place.model.to_json(), f)
        self.place.model.save_weights(f"./temp/place_weights_{key}.h5")
        with open(f"./temp/move_config_{key}.json", 'w') as f:
            json.dump(self.move.model.to_json(), f)
        self.place.model.save_weights(f"./temp/move_weights_{key}.h5")

    def train(self, board, vv):
        if board.placing or board.turns == 0:
            self.place.model.fit(board.canonical, vv)
        else:
            self.move.model.fit(board.canonical, vv)
