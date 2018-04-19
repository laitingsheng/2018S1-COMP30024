import numpy
from operator import itemgetter

from Cell import CellFactory


class Player:
    __slots__ = "board", "mine", "oppo"

    def __init__(self, player):
        self.mine = colour
        self.oppo = "@" if colour == "O" else "O"

        # initialise of board
        self.board = numpy.full((8, 8), CellFactory.create('-'), numpy.object)
        self.board[[(0, 0), (0, 7), (7, 0), (7, 7)]] = CellFactory.create('X')

        # maximum 12 pieces
        self.pieces = {'O': [None] * 12, '@': [None] * 12}
        self.num_pieces = {'O': 0, '@': 0}

        # for board shrinking
        self.placing = True
        self.turn = 0
        self.border = 0

    def _check_elim(self, row, col):
        ps = []
        poss = []
        p = self.board[(row, col)]
        s = self.border

        # eliminate opponent of current piece if applicable
        if s + 1 < row < 8 - s:  # up
            np = (row - 1, col)
            p1, p2 = self.board[[np, (row - 2, col)]]
            if p1 == p.opponent and (p2 == p.sym or p2 == 'X'):
                poss.append(np)
                ps.append(p1)
        if s - 1 < row < 6 - s:  # down
            np = (row + 1, col)
            p1, p2 = self.board[[np, (row + 2, col)]]
            if p1 == p.opponent and (p2 == p.sym or p2 == 'X'):
                poss.append(np)
                ps.append(p1)
        if s + 1 < col < 8 - s:  # left
            np = (row, col - 1)
            p1, p2 = self.board[[np, (row, col - 2)]]
            if p1 == p.opponent and (p2 == p.sym or p2 == 'X'):
                poss.append(np)
                ps.append(p1)
        if s - 1 < col < 6 - s:  # right
            np = (row, col + 1)
            p1, p2 = self.board[[np, (row, col + 2)]]
            if p1 == p.opponent and (p2 == p.sym or p2 == 'X'):
                poss.append(np)
                ps.append(p1)
        self.board[poss] = CellFactory.create('-')
        for i in ps:
            self._delete_rec(i)

        # check if itself is eliminated
        elim = False
        if s < row < 7 - s:
            p1, p2 = self.board[[(row - 1, col), (row + 1, col)]]
            if (p1 == p.opponent or p1 == 'X') and \
               (p2 == p.opponent or p2 == 'X'):
                elim = True
        if not elim and s < col < 7 - s:
            p1, p2 = self.board[[(row, col - 1), (row, col + 1)]]
            if (p1 == p.opponent or p1 == 'X') and \
               (p2 == p.opponent or p2 == 'X'):
                elim = True
        if elim:
            self.board[(row, col)] = CellFactory.create('-')
            self._delete_rec(p)

    def _delete_rec(self, p, *args):
        self.pieces[p.sym][p.num] = None
        self.num_pieces[p.sym] -= 1

    def _shrink(self):
        b = self.border
        for i in range(b, 8 - b):
            pos = [(b, i), (7 - i, b), (7 - b, 7 - i), (i, 7 - b)]
            ps = self.board[pos]
            self.board[pos] = '#'
            numpy.apply_over_axes(self._delete_rec, ps, 0)
        self.border += 1

    def _shrink_edge(self, b):

    def action(self, turns):
        pass

    def update(self, action):
        pass
