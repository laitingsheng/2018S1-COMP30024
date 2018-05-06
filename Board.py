import numpy as np


class Board:
    __slots__ = "board", "border", "n_pieces", "pieces", "turns", "placing"

    dirs = (0, -1), (1, 0), (0, 1), (-1, 0)
    mappings = 'O', '@', '-', 'X', '#'
    oppo = (1, 3), (0, 3)
    turn_thres = 128, 192

    @property
    def copy(self):
        b = object.__new__(Board)
        b.board = self.board.copy()
        b.pieces = [i.copy() for i in self.pieces]
        b.n_pieces = [i for i in self.n_pieces]
        b.border = self.border
        b.turns = self.turns
        b.placing = self.placing
        return b

    @property
    def canonical(self):
        type = self.turns % 2
        cb = self.pieces[type] - self.pieces[1 - type]

        if self.placing and type:
            cb = np.flipud(cb)

        return cb.reshape((1, 64))

    @property
    def end(self):
        return self.turns == 256 or \
               not self.placing and any(i < 2 for i in self.n_pieces)

    @property
    def reward(self):
        type = self.turns % 2
        return self.n_pieces[type] - self.n_pieces[1 - type]

    @property
    def valid_move(self):
        vm = np.zeros((8, 8, 8), np.int8)
        for y, x in np.argwhere(self.pieces[self.turns % 2] != 0):
            for i, (dx, dy) in enumerate(self.dirs):
                nx, ny = x + dx, y + dy
                if self._inboard(nx, ny) and self.board[ny, nx] == 2:
                    vm[y, x, 2 * i] = True
                    continue

                nx += dx
                ny += dy
                if self._inboard(nx, ny) and self.board[ny, nx] == 2:
                    vm[y, x, 2 * i + 1] = True

        return vm.ravel()

    @property
    def valid_place(self):
        vp = (self.board == 2).astype(np.int8)
        if self.turns % 2:
            vp = np.flipud(vp)
        return vp[:6].ravel()

    def __init__(self):
        # initialise of board
        self.board = np.full((8, 8), 2, np.uint8)
        self.board[(0, 0, 7, 7), (0, 7, 0, 7)] = 3

        # maximum 12 pieces
        self.pieces = [np.zeros((8, 8), np.int8) for _ in range(2)]
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

    def _fliplr(self):
        b = object.__new__(Board)
        b.board = np.fliplr(self.board).copy()
        b.pieces = [np.fliplr(i).copy() for i in self.pieces]
        b.n_pieces = [i for i in self.n_pieces]
        b.border = self.border
        b.turns = self.turns
        b.placing = self.placing
        return b

    def _inboard(self, x, y):
        b = self.border
        return b <= x < 8 - b and b <= y < 8 - b

    def _rot90(self, k=1):
        board = np.rot90(self.board, k)

        if self.placing and \
           ((board[:2, :] == 1).any() or (board[6:, :] == 0).any()):
            return None

        b = object.__new__(Board)
        b.board = board.copy()
        b.pieces = [np.rot90(i, k).copy() for i in self.pieces]
        b.n_pieces = [i for i in self.n_pieces]
        b.border = self.border
        b.turns = self.turns
        b.placing = self.placing
        return b

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

    def forfeit_move(self):
        if self.valid_move.sum() > 0:
            raise "invalid forfeit"

        self.turns += 1
        if self.turns in self.turn_thres:
            self._shrink()

    def interpret_move(self, a):
        y = a // 64
        x = a % 64 // 8
        i = a % 64 % 8
        dx, dy = board.dirs[i // 2]
        i = i % 2 + 1
        nx = x + dx * i
        ny = y + dy * i
        self.move(x, y, nx, ny)
        return (x, y), (nx, ny)

    def interpret_place(self, a):
        if self.turns % 2:
            # the board was flipped, so the given action is flipped as well
            a += (7 - a // 8 * 2) * 8
        y = a // 8
        x = a % 8
        self.place(x, y)
        return x, y

    def move(self, sx, sy, dx, dy):
        if sx - dx != 0 and sy - dy != 0 or \
           not (self._inboard(sx, sy) and self._inboard(dx, dy)):
            raise "invalid move"
        if self.board[dy, dx] != 2:
            raise "invalid destination"
        if abs(sx - dx) > 2 or abs(sy - dy) > 2:
            raise "invalid jump"

        t = self.board[sy, sx]
        if t != self.turns % 2:
            raise "invalid type"
        if abs(sx - dx) == 2:
            x = (sx + dx) // 2
            if self.board[sy, x] == 2:
                raise "invalid jump"
        elif abs(sy - dy) == 2:
            y = (sy + dy) // 2
            if self.board[y, sx] == 2:
                raise "invalid jump"

        self.board[(sy, dy), (sx, dx)] = self.board[(dy, sy), (dx, sx)]
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
        t = self.turns % 2
        if self.board[y, x] != 2:
            raise "not empty"
        if t == 0 and y > 5 or t == 1 and y < 2:
            raise "invalid position"

        self.board[y, x] = t
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
