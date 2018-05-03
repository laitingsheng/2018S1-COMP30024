import json
import numpy as np
from keras.models import model_from_json


if __name__ == "__main__":
    with open('./temp/place_config.json', 'r') as f:
        model = model_from_json(json.load(f))
    model.load_weights('./temp/place_weights_curr.h5')
    for i, weights in enumerate(model.get_weights()):
        weights.tofile(f"./para/place_weights_{i}.bin", sep=':')

    with open('./temp/move_config.json', 'r') as f:
        model = model_from_json(json.load(f))
    model.load_weights('./temp/move_weights_curr.h5')
    for i, weights in enumerate(model.get_weights()):
        weights.tofile(f"./para/move_weights_{i}.bin", sep=':')
