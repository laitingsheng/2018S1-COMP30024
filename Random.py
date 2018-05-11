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

        self.board = Board()

    def _move(self):
        moves = [
            (src, dest) for src, dests in self.board.valid_move(self.mine)
            for dest in dests
        ]
        if not moves:
            return None
        return choice(moves)

    def _place(self):
        return choice(list(self.board.valid_place(self.mine)))

    def action(self, turns):
        if self.board.count[self.mine] < 12:
            action = self._place()
            self.board.place(*action, self.mine)
            return action
        action = self._move()
        if action is None:
            self.board.forfeit_move()
            return
        src, dest = action
        self.board.move(*src, *dest)
        return action

    def update(self, action):
        if self.board.count[self.oppo] < 12:
            self.board.place(*action, self.oppo)
        elif action is None:
            self.board.forfeit_move()
        else:
            src, dest = action
            self.board.move(*src, *dest)
