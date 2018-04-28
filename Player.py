import numpy as np
from random import choice

from Board import Board
from Evaluation import Evaluation


class Player:
    __slots__ = "board", "depth", "model"

    def __init__(self, colour=None, board=None, depth=4, model=Evaluation()):
        if board is None:
            self.board = Board()
        else:
            self.board = board
        self.depth = depth
        self.model = model

    def _eval(self, board):
        return self.model.eval(board.feature_vector)

    def _move(self, rv=False):
        board = self.board
        best = -2
        s = None
        for src, dests in board.valid_move:
            for dest in dests:
                b = board.copy
                b.move(*src, *dest)
                re = self._eval(b)
                if re > best:
                    best = re
                    s, d = src, dest

        if not rv:
            if s is None:
                return None
            return s, d

        # forfeit move
        if s is None:
            r = board.reward()
            if r is None:
                return None, self._eval(board)
            return None, r
        return (s, d), best

    def _move_random(self):
        moves = [
            (src, dest) for src, dests in self.board.valid_move
            for dest in dests
        ]
        if not moves:
            return None
        return choice(moves)

    def _place(self, rv=False):
        board = self.board
        best = -2
        for pos in board.valid_place:
            b = board.copy
            b.place(*pos)
            re = self._eval(b)
            if re > best:
                best = re
                p = pos

        if not rv:
            return p
        return p, best

    def _place_random(self):
        return choice(list(self.board.valid_place))

    def action(self, turns):
        if self.board.placing:
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
