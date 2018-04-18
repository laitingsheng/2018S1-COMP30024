from Piece import CellFactory


class Board:
    def __init__(self, player):
        # initialise of board
        self.board = [CelllFactory.create('-')] * 64
        self.empty = [True] * 64
        self.board[0] = self.board[7] = self.board[56] = self.board[63] \
            = CellFactory.create('X')

        self.mine_type = player.mine
        self.oppo_type = player.oppo

        # maximum 12 pieces
        self.mine = [0] * 12
        self.oppo = [0] * 12
        self.num_mine = 0
        self.num_oppo = 0

        # for board shrinking
        self.turn = 0
        self.size = 8

    def __repr__(self):
        re = ""
        i = 1
        for l in self.board:
            re += repr(l)
            i += 1
            if i % 9 == 0:
                re += '\n'
                i = 1
        return re[:-1]

    def __str__(self):
        return self.board.__str__()

    @staticmethod
    def _from_coor(row, column):
        return 8 * row + column

    @staticmethod
    def _from_index(index):
        # (row, column)
        return int(math.floor(index / 8)), index % 8

    def _check_elim(self, pos):
        pass

    def place(self, pos, piece):
        self.board[pos] = piece
        self._check_elim(pos)

    def move(self, src, dest):
        self.board[src], self.board[dest] = self.board[dest], self.board[src]
        self._check_elim(dest)
