from Board import Board


inf = float("inf")


class Player:
    __slots__ = "board", "depth", "mine", "oppo", "turn_step", "turn_thres"

    @staticmethod
    def _sum_test(li):
        return sum(li) > 1

    def __init__(self, colour, depth=5):
        if colour == 'O':
            self.mine = 0x0
            self.oppo = 0x10
        else:
            self.mine = 0x10
            self.oppo = 0x0

        self.board = Board()
        self.depth = 1 if depth < 1 else depth
        self.turn_thres = self.turn_step = 128

    def _eval(self, board, turns):
        pass

    def _move(self, turns):
        board = self.board
        alpha = -inf
        for src, dests in board.valid_move(self.mine // 0x10):
            for dest in dests:
                b = board.copy()
                b.move(*src, *dests)
                re = self._move_min(board, 1, turns, alpha, inf)
                if re > alpha:
                    alpha = re
                    s, d = src, dest

        self.board.move(*s, *d)
        return s, d

    def _move_max(self, board, depth, turns, alpha, beta):
        if depth == self.depth or any(i < 2 for i in board.num_pieces):
            return self._eval(board, turns)

        for src, dests in board.valid_move(self.mine // 0x10):
            for dest in dests:
                b = board.copy()
                b.move(*src, *dests)
                re = self._move_min(board, depth, turns, alpha, beta)
                if re > alpha:
                    alpha = re
                    if alpha >= beta:
                        return beta
        return alpha

    def _move_min(self, board, depth, turns, alpha, beta):
        if depth == self.depth or any(i < 2 for i in board.num_pieces):
            return self._eval(board, turns)

        for src, dests in board.valid_move(self.oppo // 0x10):
            for dest in dests:
                b = board.copy()
                b.move(*src, *dests)
                re = self._move_max(board, depth, turns, alpha, beta)
                if re < alpha:
                    beta = re
                    if beta <= alpha:
                        return beta
        return beta

    def _place(self):
        pos = self._place_search(self.depth)
        self.board.place(*pos, self.mine)
        self.mine += 1
        return pos

    def _place_max(self, board, depth, alpha, beta):
        if board.num_pieces[self.mine // 0x10] == 12:
            return self._move_max(board, depth, 0, alpha, beta)

    def _place_min(self, board, depth, alpha, beta):
        if board.num_pieces[self.oppo // 0x10] == 12:
            return self._move_min(board, depth, 0, alpha, beta)

    def action(self, turns):
        if self.mine < 12:
            return self._place()

        return self._move(turns)

    def update(self, action):
        if self.mine < 12:
            self.board.place(*action, self.oppo)
            self.oppo += 1
        else:
            src, dest = action
            self.board.move(*src, *dest)
