import sys
import numpy as np
from random import choice

from Board import Board
from Evaluation import Evaluation

inf = float("inf")


class Player:
    __slots__ = "board", "depth", "model"

    def __init__(self, colour=None, load=False):
        self.board = Board()
        self.model = Evaluation(load)

    def _move(self):
        vm = self.board.valid_move
        if vm.sum() < 1:
            return self.board.forfeit_move()

        pi = self.model.predict(self.board)[0]
        pi[vm == 0] = -inf
        return self.board.interpret_move(np.argmax(pi))

    def _place(self):
        pi = self.model.predict(self.board)[0]
        pi[self.board.valid_place == 0] = -inf
        return self.board.interpret_place(np.argmax(pi))

    def _execute(self, board, decay, ep):
        hist = []

        while not board.end:
            if board.placing:
                vp = board.valid_place
                if np.random.rand() <= ep:
                    a = np.random.choice(64, p=vp / vp.sum())
                else:
                    pi = self.model.predict(board)[0]
                    pi[vp == 0] = -inf
                    a = np.argmax(pi)
                b = board.copy
                board.interpret_place(a)
                hist.append((b, a, board.reward(b)))
            else:
                vm = board.valid_move
                if vm.sum() < 1:
                    board.forfeit_move()
                else:
                    if np.random.rand() <= ep:
                        a = np.random.choice(512, p=vm / vm.sum())
                    else:
                        pi = self.model.predict(board)[0]
                        pi[vm == 0] = -inf
                        a = np.argmax(pi)
                    b = board.copy
                    board.interpret_move(a)
                    hist.append((b, a, board.reward(b)))

        s = 0
        pb, pa, pr = hist[0]
        pvv = self.model.predict(pb)
        for b, a, r in hist[1:]:
            vv = self.model.predict(b)
            pvv[0, pa] = pr + decay * np.argmax(vv[0])
            self.model.train(pb, pvv)
            pb, pa, pr, pvv = b, a, r, vv
        pvv[0, pa] = pr
        self.model.train(pb, pvv)

    def action(self, turns):
        if self.board.placing:
            return self._place()
        return self._move()

    def save(self, suffix="curr"):
        self.model.save(suffix)

    def train(self, episode, decay=0.95):
        print('-' * 8, "Episode", episode, '-' * 8, file=sys.stderr)
        ep = 1
        while ep > 0.01:
            self._execute(Board(), decay, ep)
            ep *= 0.995

    def update(self, action):
        if self.board.placing:
            self.board.place(*action)
        elif action is None:
            self.board.forfeit_move()
        else:
            src, dest = action
            self.board.move(*src, *dest)
