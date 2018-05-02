import numpy as np
from random import choice

from Board import Board
from Evaluation import Evaluation


class Player:
    __slots__ = "board", "depth", "model"

    def __init__(self, colour=None):
        self.board = Board()
        self.model = Evaluation()

    def _move(self, rv=False):
        board = self.board
        vm = board.valid_move
        if vm.sum() < 1:
            if rv:
                return None, None
            return None

        pi = self.model.eval(vm, False)
        a = np.argmax(pi)
        if rv:
            return a, pi
        return a

    def _place(self, rv=False):
        pi = self.model.eval(self.board.valid_place, True)
        a = np.argmax(pi)
        if rv:
            return a, pi
        return a

    def _search(self, board, hist, la):
        if board.end:
            r = board.reward
            s = 0
            pv, pa, pb, pvv = hist[0]
            for v, a, b, vv in hist[1:]:
                if a > -1:
                    s += la * (v - pv)
                    la *= la
                    pvv[0, pa] = r + s * pv
                    self.model.train(pb, pvv)
                pv, pa, pb, pvv = v, a, b, vv

            s += la * (r - pv)
            pvv[0, pa] = r + s * pv
            self.model.train(pb, pvv)
            return

        if board.placing:
            vp = board.valid_place
            vvp = self.model.predict(board)
            for a in np.argwhere(vp):
                a = a[0]
                v = vvp[0, a]
                b = board.copy
                b.place(a % 8, a // 8)
                hist.append((v, a, b, vvp.copy()))
                self._search(b, hist, la)
                hist.pop()
        else:
            vm = board.valid_move
            if vm.sum() < 1:
                b = board.copy
                b.forfeit_move()
                hist.append((1, -1, b, None))
                self._search(b, hist, la)
                hist.pop()
            else:
                vvm = self.model.predict(board)
                for a in np.argwhere(vm):
                    a = a[0]
                    v = vvm[0, a]
                    b = board.copy
                    y = a // 64
                    x = a % 64 // 8
                    i = a % 64 % 8
                    dx, dy = b.dirs[i // 2]
                    i = i % 2 + 1
                    nx = x + dx * i
                    ny = y + dy * i
                    b.move(x, y, nx, ny)
                    hist.append((v, a, b, vvm.copy()))
                    self._search(b, hist, la)
                    hist.pop()

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

    def save(self, key):
        self.model.save(key)

    def train(self, episode, la=0.7):
        print('-' * 8, "Episode", episode, '-' * 8)
        self._search(Board(), [], la)

    def update(self, action):
        if self.board.placing:
            self.board.place(*action)
        elif action is None:
            self.board.forfeit_move()
        else:
            src, dest = action
            self.board.move(*src, *dest)
