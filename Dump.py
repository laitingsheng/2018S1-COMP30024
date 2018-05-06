import json
import numpy as np
from keras.models import model_from_json
from Pretrained import PlaceModel, MoveModel


if __name__ == "__main__":
    with open('./temp/place_config.json', 'r') as f:
        pmodel = model_from_json(json.load(f))
    pmodel.load_weights('./temp/place_weights_best.h5')
    for i, weights in enumerate(pmodel.get_weights()):
        np.save(f"./pretrained/place_weights_{i}", weights)

    with open('./temp/move_config.json', 'r') as f:
        mmodel = model_from_json(json.load(f))
    mmodel.load_weights('./temp/move_weights_best.h5')
    for i, weights in enumerate(mmodel.get_weights()):
        np.save(f"./pretrained/move_weights_{i}", weights)
