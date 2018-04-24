from itertools import product


class Board:
    """
        The board stored internally in player

        Representations of pieces (for minimal storage and fast comparison):
        0x00 - 0x0C: represents white pieces ('O') with numbering
        0x10 - 0x1C: represents black pieces ('@') with numbering
        0x20       : represents space '-'
        0x30       : represents block 'X'
        0x40       : represents position which has been removed in shrinking

        The __slots__ prevents the creation of __dict__ which can further
        decrease the memory usage of this object and fast access of members

        valid_move and valid_place return iterator for minimal storage
        requirement and fast access, so call copy() before altering the board,
        or otherwise the behaviour is undefined
    """

    __slots__ = "board", "border", "count", "n_pieces", "pieces", "turns"

    mappings = 'O', '@', '-', 'X', '#'
    oppo = (1, 3), (0, 3)
    dirs = (0, -1), (1, 0), (0, 1), (-1, 0)
    turn_thres = 128, 192

    def __init__(self):
        # initialise of board
        board = [[0x20] * 8 for _ in range(8)]
        board[0][0] = board[0][7] = board[7][0] = board[7][7] = 0x30
        self.board = board

        # maximum 12 pieces
        self.count = [0, 0]
        self.pieces = [[None] * 12, [None] * 12]
        self.n_pieces = [0, 0]

        # record number of shrinks
        self.border = 0
        self.turns = 0

    def __repr__(self):
        return '[' + ",\n ".join(
            '[' + ' '.join(
                self.mappings[x // 0x10] for x in y
            ) + ']' for y in self.board
        ) + ']'

    def __str__(self):
        return '[' + ','.join(
            '[' + ' '.join(
                self.mappings[x // 0x10] for x in y
            ) + ']' for y in self.board
        ) + ']'

    def _add_rec(self, p, pos):
        t = p // 0x10
        self.pieces[t][p % 0x10] = pos
        self.n_pieces[t] += 1

    def _elim(self, x, y):
        board = self.board
        for dx, dy in self.dirs:
            nx, ny = x + dx, y + dy
            if self._surrounded(nx, ny, dx, dy):
                self._delete_rec(board[ny][nx])
                board[ny][nx] = 0x20

    def _delete_rec(self, p):
        if p >= 0x20:
            return
        t = p // 0x10
        self.pieces[t][p % 0x10] = None
        self.n_pieces[t] -= 1

    def _inboard(self, x, y):
        b = self.border
        return b <= x < 8 - b and b <= y < 8 - b

    def _shrink(self):
        b = self.border
        board = self.board

        # first shrink the edges
        for i in range(b, 7 - b):
            for x, y in ((b, i), (7 - i, b), (7 - b, 7 - i), (i, 7 - b)):
                self._delete_rec(board[y][x])
                board[y][x] = 0x40

        # determine if the shrinking leads to eliminations of current pieces
        b += 1
        for x, y in ((b, b), (b, 7 - b), (7 - b, 7 - b), (7 - b, b)):
            self._delete_rec(board[y][x])
            board[y][x] = 0x30
            self._elim(x, y)

        self.border = b

    def _surrounded(self, x, y, dx, dy):
        if not self._inboard(x, y):
            return False

        board = self.board
        t = board[y][x] // 0x10
        # ignore '-'
        if t > 1:
            return False

        x1, y1 = x + dx, y + dy
        if not self._inboard(x1, y1):
            return False
        x2, y2 = x - dx, y - dy
        if not self._inboard(x2, y2):
            return False
        t1 = board[y1][x1] // 0x10
        t2 = board[y2][x2] // 0x10
        oppo = self.oppo[t]
        return t1 in oppo and t2 in oppo

    def _try_move(self, x, y, dx, dy):
        board = self.board

        # move 1 step and test
        nx, ny = x + dx, y + dy
        if not self._inboard(nx, ny) or board[ny][nx] == 0x30:
            return None
        if board[ny][nx] == 0x20:
            return nx, ny

        # perform a jump if possible
        nx += dx
        ny += dy
        if self._inboard(nx, ny) and board[ny][nx] == 0x20:
            return nx, ny

    def copy(self):
        # create without initialisation
        b = object.__new__(Board)
        # deepcopy
        b.board = [[i for i in j] for j in self.board]
        b.count = [i for i in self.count]
        b.pieces = [[i for i in j] for j in self.pieces]
        b.n_pieces = [i for i in self.n_pieces]
        b.border = self.border
        b.turns = self.turns
        return b

    def move(self, sx, sy, dx, dy):
        board = self.board
        board[sy][sx], board[dy][dx] = board[dy][dx], board[sy][sx]
        p = board[dy][dx]

        self._elim(dx, dy)
        if self._surrounded(dx, dy, 1, 0) or self._surrounded(dx, dy, 0, 1):
            board[dy][dx] = 0x20
            self._delete_rec(p)
        else:
            self.pieces[p // 0x10][p % 0x10] = (dx, dy)

        self.turns += 1
        if self.turns in self.turn_thres:
            self._shrink()

    def place(self, x, y, type):
        board = self.board
        piece = type * 0x10 + self.count[type]
        self.count[type] += 1

        board[y][x] = piece
        self._elim(x, y)
        # the piece is eliminated immediately, no manipulation of record
        if self._surrounded(x, y, 1, 0) or self._surrounded(x, y, 0, 1):
            board[y][x] = 0x20
        # add record with respect to this piece
        else:
            self._add_rec(piece, (x, y))

    def pot_hole(self, x, y, type):
        board = self.board
        oppo = self.oppo[type]

        x1, x2 = x - 1, x + 1
        if self._inboard(x1, y) and self._inboard(x2, y):
            t1, t2 = board[y][x1] // 0x10, board[y][x2] // 0x10
            if t1 in oppo and t2 != type or t2 in oppo and t1 != type:
                return True

        y1, y2 = y - 1, y + 1
        if self._inboard(x, y1) and self._inboard(x, y2):
            t1, t2 = board[y1][x] // 0x10, board[y2][x] // 0x10
            if t1 in oppo and t2 != type or t2 in oppo and t1 != type:
                return True

        return False

    def pot_surrounded(self, x, y):
        board = self.board
        t = board[y][x] // 0x10
        oppo = self.oppo[t]

        x1, x2 = x - 1, x + 1
        if self._inboard(x1, y) and self._inboard(x2, y):
            t1, t2 = board[y][x1] // 0x10, board[y][x2] // 0x10
            if t1 in oppo and t2 == 2 or t2 in oppo and t1 == 2:
                return True

        y1, y2 = y - 1, y + 1
        if self._inboard(x, y1) and self._inboard(x, y2):
            t1, t2 = board[y1][x] // 0x10, board[y2][x] // 0x10
            if t1 in oppo and t2 == 2 or t2 in oppo and t1 == 2:
                return True

        return False

    def valid_place(self, type):
        # black piece
        if type:
            return (
                (x, y) for x, y in product(range(8), range(2, 8))
                if self.board[y][x] == 0x20
            )
        # white piece
        return (
            (x, y) for x, y in product(range(8), range(6))
            if self.board[y][x] == 0x20
        )

    def valid_move(self, type):
        return (((x, y), filter(
            None, (self._try_move(x, y, dx, dy) for dx, dy in self.dirs)
        )) for x, y in filter(None, self.pieces[type]))

    def end(self):
        return any(i < 2 for i in self.n_pieces)
