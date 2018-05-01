from collections import Counter
from random import choice

from Board import Board


class Player:
    def __init__(self, colour):
        if colour == "white":
            self.mine = 0
            self.oppo = 1
        else:
            self.mine = 1
            self.oppo = 0

    def _move(self):
        moves = [
            (src, dest) for src, dests in self.board.valid_move
            for dest in dests
        ]
        if not moves:
            return None
        return choice(moves)

    def _place(self):
        return choice(list(self.board.valid_place))

    def action(self, turns):
        if self.board.count[]:
            action = self._place()
            self.board.place(*action)
            return action
        action = self._move()
        if action is None:
            self.board.forfeit_move()
            return
        src, dest = action
        self.board.move(*src, *dest)
        return action

    def update(self, action):
        if self.board.placing:
            self.board.place(*action)
        elif action is None:
            self.board.forfeit_move()
        else:
            src, dest = action
            self.board.move(*src, *dest)
