import numpy


class Player:
    __slots__ = "board", "mine"

    def __init__(self, colour):
        self.mine = 0 if colour == 'O' else 1

    def action(self, turns):
        pass

    def update(self, action):
        pass
