import numpy as np
from itertools import product


class Board:
    __slots__ = "board", "border", "n_pieces", "pieces", "turns", "placing"

    dirs = (0, -1), (1, 0), (0, 1), (-1, 0)
    mappings = 'O', '@', '-', 'X', '#'
    oppo = (1, 3), (0, 3)
    turn_thres = 128, 192

    @property
    def copy(self):
        # create without initialisation
        b = object.__new__(Board)
        # deepcopy
        b.board = self.board.copy()
        b.pieces = [i.copy() for i in self.pieces]
        b.n_pieces = [i for i in self.n_pieces]
        b.border = self.border
        b.turns = self.turns
        b.placing = self.placing
        return b

    @property
    def feature_vector(self):
        fv = np.zeros((1, 259), np.uint8)
        fv[0, :64] = self.pieces[0].ravel()
        fv[0, 64:128] = self.pieces[1].ravel()

        if self.placing:
            s = self.board == 2
            if self.turns % 2:
                s[:2, :] = False
            else:
                s[6:, :] = False
            fv[0, 128:192] = s.ravel()
        else:
            s = np.zeros((8, 8), np.uint8)
            for (sx, sy), dests in self.valid_move:
                for (dx, dy) in dests:
                    s[(sy, dy), (sx, dx)] += 1
            fv[0, 192:256] = s.ravel()
        fv[0, 256] = self.turns % 2
        fv[0, 257] = self.placing
        fv[0, 258] = self.turns // 2 + 1
        return fv

    @property
    def valid_place(self):
        if self.turns % 2:
            return (
                (x, y) for x, y in product(range(8), range(2, 8))
                if self.board[y, x] == 2
            )
        return (
            (x, y) for x, y in product(range(8), range(6))
            if self.board[y, x] == 2
        )

    @property
    def valid_move(self):
        return (((x, y), filter(
            None, (self._try_move(x, y, dx, dy) for dx, dy in self.dirs)
        )) for y, x in np.argwhere(self.pieces[self.turns % 2] != 0))

    def __init__(self):
        # initialise of board
        self.board = np.full((8, 8), 2, np.uint8)
        self.board[(0, 0, 7, 7), (0, 7, 0, 7)] = 3

        # maximum 12 pieces
        self.pieces = [np.zeros((8, 8), np.bool) for _ in range(2)]
        self.n_pieces = [0, 0]

        # record number of shrinks
        self.border = 0
        self.turns = 0
        self.placing = True

    def __repr__(self):
        return '[' + ",\n ".join(
            '[' + ' '.join(
                self.mappings[x] for x in y
            ) + ']' for y in self.board
        ) + ']'

    def __str__(self):
        return '[' + ','.join(
            '[' + ' '.join(
                self.mappings[x] for x in y
            ) + ']' for y in self.board
        ) + ']'

    def _add_rec(self, x, y):
        t = self.board[y, x]
        self.pieces[t][y, x] = True
        self.n_pieces[t] += 1

    def _delete_rec(self, x, y):
        t = self.board[y, x]
        if t > 1:
            return
        self.pieces[t][y, x] = False
        self.n_pieces[t] -= 1

    def _elim(self, x, y):
        for dx, dy in self.dirs:
            nx, ny = x + dx, y + dy
            if self._inboard(nx, ny) and self._surrounded(nx, ny, dx, dy):
                self._delete_rec(nx, ny)
                self.board[ny, nx] = 2

    def _inboard(self, x, y):
        b = self.border
        return b <= x < 8 - b and b <= y < 8 - b

    def _shrink(self):
        b = self.border

        # first shrink the edges
        for i in range(b, 7 - b):
            for x, y in ((b, i), (7 - i, b), (7 - b, 7 - i), (i, 7 - b)):
                self._delete_rec(x, y)
                self.board[y, x] = 4

        # determine if the shrinking leads to eliminations of current pieces
        b += 1
        for x, y in ((b, b), (b, 7 - b), (7 - b, 7 - b), (7 - b, b)):
            self._delete_rec(x, y)
            self.board[y, x] = 3
            self._elim(x, y)

        self.border = b

    def _surrounded(self, x, y, dx, dy):
        t = self.board[y, x]
        # ignore '-'
        if t > 1:
            return False

        x1, y1 = x + dx, y + dy
        if not self._inboard(x1, y1):
            return False
        x2, y2 = x - dx, y - dy
        if not self._inboard(x2, y2):
            return False
        t1, t2 = self.board[(y1, y2), (x1, x2)]
        oppo = self.oppo[t]
        return t1 in oppo and t2 in oppo

    def _try_move(self, x, y, dx, dy):
        # move 1 step and test
        x += dx
        y += dy
        if not self._inboard(x, y) or self.board[y, x] == 3:
            return None
        if self.board[y, x] == 2:
            return x, y

        # perform a jump if possible
        x += dx
        y += dy
        if self._inboard(x, y) and self.board[y, x] == 2:
            return x, y

    def forfeit_move(self):
        self.turns += 1
        if self.turns in self.turn_thres:
            self._shrink()

    def move(self, sx, sy, dx, dy):
        self.board[(sy, dy), (sx, dx)] = self.board[(dy, sy), (dx, sx)]
        t = self.board[dy, dx]
        self.pieces[t][sy, sx] = False

        self._elim(dx, dy)
        if self._surrounded(dx, dy, 1, 0) or self._surrounded(dx, dy, 0, 1):
            self.n_pieces[t] -= 1
            self.board[dy, dx] = 2
        else:
            self.pieces[t][dy, dx] = True

        self.turns += 1
        if self.turns in self.turn_thres:
            self._shrink()

    def place(self, x, y):
        self.board[y, x] = self.turns % 2
        self._elim(x, y)
        # the piece is eliminated immediately, no manipulation of record
        if self._surrounded(x, y, 1, 0) or self._surrounded(x, y, 0, 1):
            self.board[y, x] = 2
        # add record with respect to this piece
        else:
            self._add_rec(x, y)

        self.turns += 1
        if self.turns == 24:
            self.turns = 0
            self.placing = False

    def reward(self):
        type = self.turns % 2
        oppo = 1 - type
        if not self.placing:
            if self.n_pieces[type] < 2 and self.n_pieces[oppo] < 2:
                return 0
            if self.n_pieces[oppo] < 2:
                return 1
            if self.n_pieces[type] < 2:
                return -1
        if self.turns == 256:
            dif = self.n_pieces[type] - self.n_pieces[oppo]
            if dif > 0:
                return 1
            elif dif < 0:
                return -1
            return 0
        return None
