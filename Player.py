import sys
import numpy as np
from random import choice, shuffle

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
            b = board.copy
            if board.placing:
                vp = board.valid_place
                if np.random.rand() <= ep:
                    a = np.random.choice(48, p=vp / vp.sum())
                else:
                    pi = self.model.predict(board)[0]
                    pi[vp == 0] = -inf
                    a = np.argmax(pi)
                fb, fa = b.fliplr(), a // 8 * 8 + (7 - a % 8)
                board.interpret_place(a)
                nb = board.copy
                fnb = nb.fliplr()
                hist.extend([
                    (b, a, board.reward, nb), (fb, fa, board.reward, fnb)
                ])
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
                    fb = b.fliplr()
                    y = a // 64
                    x = a % 64 // 8
                    i = a % 64 % 8
                    if i in (2, 3, 6, 7):
                        i = (i + 4) % 8
                    fa = y * 64 + (7 - x) * 8 + i
                    board.interpret_move(a)
                    nb = board.copy
                    fnb = nb.fliplr()
                    hist.extend([
                        (b, a, board.reward, nb), (fb, fa, board.reward, fnb)
                    ])
            b = nb

        shuffle(hist)
        for b, a, r, nb in hist:
            t = r
            if not nb.end:
                t += decay * np.argmax(self.model.predict(nb)[0])
            vv = self.model.predict(b)
            vv[0, a] = t
            self.model.train(b, vv)

    def action(self, turns):
        if self.board.placing:
            return self._place()
        return self._move()

    def save(self, key, suffix="curr"):
        self.model.save(key, suffix)

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
