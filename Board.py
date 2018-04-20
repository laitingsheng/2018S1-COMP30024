class Board:
    mappings = ['O', '@', '-', 'X', '#']

    @classmethod
    def _conv(cls, r):
        return cls.mappings[r // 0x10]

    @classmethod
    def _line_print(cls, x):
        return '[' + ' '.join(map(cls._conv, x)) + ']'

    def __init__(self):
        # initialise of board
        board = [[0x20] * 8 for _ in range(8)]
        board[0][0] = board[0][7] = board[7][0] = board[7][7] = 0x30
        self.board = board

        # maximum 12 pieces
        self.pieces = [[None] * 12, [None] * 12]
        self.oppo = [(1, 3), (0, 3)]
        self.num_pieces = [0, 0]

        # for board shrinking
        self.border = 0

    def __repr__(self):
        return '[' + ",\n ".join(map(self._line_print, self.board)) + ']'

    def __str__(self):
        return '[' + ','.join(map(self._line_print, self.board)) + ']'

    def _add_rec(self, p, pos):
        t = p // 0x10
        p %= 0x10
        self.pieces[t][p] = pos
        self.num_pieces[t] += 1

    def _elim(self, x, y):
        board = self.board
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            nx, ny = x + dx, y + dy
            if self._surrounded(nx, ny, dx, dy):
                self._delete_rec(board[nx][ny])
                board[nx][ny] = 0x20

    def _delete_rec(self, p):
        t = p // 0x10
        if t > 1:
            return
        p %= 0x10
        self.pieces[t][p] = None
        self.num_pieces[t] -= 1

    def _inboard(self, x, y):
        b = self.border
        return b - 1 < x < 8 - b and b - 1 < y < 8 - b

    def _shrink(self):
        b = self.border
        board = self.board

        for i in range(b, 7 - b):
            for x, y in ((b, i), (7 - i, b), (7 - b, 7 - i), (i, 7 - b)):
                self._delete_rec(board[x][y])
                board[x][y] = 0x40

        b += 1
        for x, y in ((b, i), (7 - i, b), (7 - b, 7 - i), (i, 7 - b)):
            self._delete_rec(board[x][y])
            board[x][y] = 0x30
            self._elim(x, y)

        self.border += b

    def _surrounded(self, x, y, dx, dy):
        x1, y1 = x + dx, y + dy
        if not self._inboard(x1, y1):
            return False
        x2, y2 = x - dx, y - dy
        if not self._inboard(x2, y2):
            return False

        board = self.board
        p = board[x][y]
        if p == 0x20:
            return False
        p1 = board[x1][y1]
        p2 = board[x2][y2]
        oppo = self.oppo[p // 0x10]
        return p1 // 0x10 in oppo and p2 // 0x10 in oppo

    def place(self, x, y, piece):
        board = self.board
        board[x][y] = piece
        self._elim(x, y)
        if self._surrounded(x, y, 1, 0) or self._surrounded(x, y, 0, 1):
            board[x][y] = 0x20
        else:
            self._add_rec(piece, (x, y))

    def move(self, sx, sy, dx, dy):
        board = self.board
        board[sx][sy], board[dx][dy] = board[dx][dy], board[sx][sy]
