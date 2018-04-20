import numpy


class Player:
    def __init__(self, colour):
        self.mine = 0 if colour == 'O' else 1
        self.placing = True
        self.turn = 0

    def action(self, turns):
        pass

    def update(self, action):
        pass
