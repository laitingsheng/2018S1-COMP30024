import numpy as np
from random import choice

from Board import Board
from Evaluation import Evaluation


class Player:
    __slots__ = "board", "depth", "model"

    def __init__(self, colour=None, depth=4, model=Evaluation()):
        self.board = Board()
        self.depth = depth
        self.model = model

    def _eval(self, board):
        return self.model.eval(board.feature_vector)

    def _move(self, rv=False):
        board = self.board
        alpha = -2
        s = None
        for src, dests in board.valid_move:
            for dest in dests:
                b = board.copy
                b.move(*src, *dest)
                re = self._move_min(b, 1, alpha, 2)
                if re > alpha:
                    alpha = re
                    s, d = src, dest

        if not rv:
            if s is None:
                return None
            return (s, d)

        # forfeit move
        if s is None:
            r = board.reward()
            if r is None:
                return None, self._eval(board)
            return None, r
        return (s, d), alpha

    def _move_max(self, board, depth, alpha, beta):
        r = board.reward()
        if r is not None:
            return r

        if depth == self.depth:
            return self._eval(board)

        depth += 1
        updated = False
        for src, dests in board.valid_move:
            for dest in dests:
                b = board.copy
                b.move(*src, *dest)
                re = self._move_min(b, depth, alpha, beta)
                if re > alpha:
                    alpha = re
                    updated = True
                    if alpha >= beta:
                        return beta

        # forfeit move
        if not updated:
            board.forfeit_move()
            return self._move_min(board, depth, alpha, beta)

        return alpha

    def _move_min(self, board, depth, alpha, beta):
        r = board.reward()
        if r is not None:
            return r

        if depth == self.depth:
            return self._eval(board)

        depth += 1
        updated = False
        for src, dests in board.valid_move:
            for dest in dests:
                b = board.copy
                b.move(*src, *dest)
                re = self._move_max(b, depth, alpha, beta)
                if re < beta:
                    beta = re
                    updated = True
                    if beta <= alpha:
                        return beta

        # forfeit move
        if not updated:
            board.forfeit_move()
            return self._move_min(board, depth, alpha, beta)

        return beta

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
        alpha = -2
        for pos in board.valid_place:
            b = board.copy
            b.place(*pos)
            re = self._place_min(b, 1, alpha, 2)
            if re > alpha:
                alpha = re
                p = pos

        if not rv:
            return p
        return p, alpha

    def _place_max(self, board, depth, alpha, beta):
        if not board.placing:
            return self._move_max(board, depth, alpha, beta)

        if depth == self.depth:
            return self._eval(board)

        depth += 1
        for pos in board.valid_place:
            b = board.copy
            b.place(*pos)
            re = self._place_min(b, depth, alpha, beta)
            if re > alpha:
                alpha = re
                if alpha >= beta:
                    return beta
        return alpha

    def _place_min(self, board, depth, alpha, beta):
        if not board.placing:
            return self._move_min(board, depth, alpha, beta)

        if depth == self.depth:
            return self._eval(board)

        depth += 1
        for pos in board.valid_place:
            b = board.copy
            b.place(*pos)
            re = self._place_max(b, depth, alpha, beta)
            if re < beta:
                beta = re
                if beta <= alpha:
                    return beta
        return beta

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
