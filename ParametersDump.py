import json
import numpy as np
from keras.models import model_from_json


if __name__ == "__main__":
    with open('./temp/place_config.json', 'r') as f:
        model = model_from_json(json.load(f))
    model.load_weights('./temp/place_weights_curr.h5')
    for weights in model.get_weights():
        np.save(f"place_weights_{i}", weights)

    with open('./temp/move_config.json', 'r') as f:
        model = model_from_json(json.load(f))
    model.load_weights('./temp/move_weights_curr.h5')
    for weights in model.get_weights():
        np.save(f"move_weights_{i}", weights)
