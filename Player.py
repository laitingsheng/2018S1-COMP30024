import numpy


class Player:
    def __init__(self, colour):
        self.mine = 0x0 if colour == 'O' else 0x10
        self.placing = True
        self.turn = 0

    def _place(self):
        pass

    def _move(self):
        pass

    def action(self, turns):
        if self.placing:
            return self._place()

    def update(self, action):
        pass
