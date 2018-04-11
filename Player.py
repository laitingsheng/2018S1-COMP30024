import numpy

class Player:
    __slots__ = "board", "mine", "oppo"

    def __init__(self, colour):
        self.mine = colour
        self.oppo = "@" if colour == "O" else "O"

    def action(self, turns):
        pass

    def update(self, action):
        pass
