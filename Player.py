import numpy

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
        dirs = [(row - 1), (), (), ()]

    def _delete_rec(self, p):
        self.pieces[p.sym][p.num] = None
        self.num_pieces[p.sym] -= 1

    def _shrink(self):
        map(self._shrink_edge, range(self.border, 8 - self.border))
        self.border += 1

    def _shrink_edge(self, b):
        pos = [(b, i), (7 - i, b), (7 - b, 7 - i), (i, 7 - b)]
        ps = self.board[pos]
        self.board[pos] = CellFactory.create('X')
        map(self._delete_rec, ps)

    def action(self, turns):
        pass

    def update(self, action):
        pass
