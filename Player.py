from Board import Board


inf = float("inf")
cm1 = cm2 = cm3 = cm5 = cp1 = cp2 = cp3 = cp5 = 1
cm4 = cm6 = cp4 = cp6 = 2


class Player:
    __slots__ = "board", "depth", "mine", "oppo", "turn_step", "turn_thres"

    def __init__(self, colour, depth=4):
        if colour == "white":
            self.mine = 0
            self.oppo = 1
        else:
            self.mine = 1
            self.oppo = 0

        self.board = Board()
        self.depth = 1 if depth < 1 else depth
        self.turn_thres = self.turn_step = 128

    def _eval_move(self, board, turns):
        re = cm1 * board.n_pieces[self.mine] - cm2 * board.n_pieces[self.oppo]

        for x, y in filter(None, board.pieces[self.mine]):
            re -= cm4 * (abs(x - 3.5) + abs(y - 3.5))

        for x, y in filter(None, board.pieces[self.oppo]):
            re += cm6 * (abs(x - 3.5) + abs(y - 3.5))

        return re

    def _eval_place(self, board):
        re = cp1 * board.n_pieces[self.mine] - cp2 * board.n_pieces[self.oppo]

        for x, y in filter(None, board.pieces[self.mine]):
            if board.pot_surrounded(x, y):
                re -= cp3
            re -= cp4 * (abs(x - 3.5) + abs(y - 3.5))

        for x, y in filter(None, board.pieces[self.oppo]):
            if board.pot_surrounded(x, y):
                re += cp5
            re += cp6 * (abs(x - 3.5) + abs(y - 3.5))

        return re

    def _move(self, turns):
        board = self.board
        alpha = -inf
        s = None
        for src, dests in board.valid_move(self.mine):
            for dest in dests:
                b = board.copy()
                b.move(*src, *dest)
                re = self._move_min(b, 1, turns, alpha, inf)
                if re > alpha:
                    alpha = re
                    s, d = src, dest

        # forfeit move
        if s is None:
            return None

        self.board.move(*s, *d)
        return s, d

    def _move_max(self, board, depth, turns, alpha, beta):
        if depth == self.depth or board.end():
            return self._eval_move(board, turns)

        depth += 1
        turns += 1
        updated = False
        for src, dests in board.valid_move(self.mine):
            for dest in dests:
                b = board.copy()
                b.move(*src, *dest)
                re = self._move_min(b, depth, turns, alpha, beta)
                if re > alpha:
                    alpha = re
                    updated = True
                    if alpha >= beta:
                        return beta

        # forfeit move
        if not updated:
            return self._move_min(board, depth, turns, alpha, beta)

        return alpha

    def _move_min(self, board, depth, turns, alpha, beta):
        if depth == self.depth or board.end():
            return self._eval_move(board, turns)

        depth += 1
        turns += 1
        updated = False
        for src, dests in board.valid_move(self.oppo):
            for dest in dests:
                b = board.copy()
                b.move(*src, *dest)
                re = self._move_max(b, depth, turns, alpha, beta)
                if re < beta:
                    beta = re
                    updated = True
                    if beta <= alpha:
                        return beta

        # forfeit move
        if not updated:
            return self._move_min(board, depth, turns, alpha, beta)

        return beta

    def _place(self):
        board = self.board
        alpha = -inf
        for pos in board.valid_place(self.mine):
            b = board.copy()
            b.place(*pos, self.mine)
            re = self._place_min(b, 1, alpha, inf)
            if re > alpha:
                alpha = re
                p = pos
        self.board.place(*p, self.mine)
        return p

    def _place_max(self, board, depth, alpha, beta):
        if board.count[self.mine] == 12:
            return self._move_max(board, depth, 0, alpha, beta)

        if depth == self.depth:
            return self._eval_place(board)

        depth += 1
        for pos in board.valid_place(self.mine):
            b = board.copy()
            b.place(*pos, self.mine)
            re = self._place_min(b, depth, alpha, beta)
            if re > alpha:
                alpha = re
                if alpha >= beta:
                    return beta
        return alpha

    def _place_min(self, board, depth, alpha, beta):
        if board.count[self.oppo] == 12:
            return self._move_min(board, depth, 0, alpha, beta)

        if depth == self.depth:
            return self._eval_place(board)

        depth += 1
        for pos in board.valid_place(self.oppo):
            b = board.copy()
            b.place(*pos, self.oppo)
            re = self._place_max(b, depth, alpha, beta)
            if re < beta:
                beta = re
                if beta <= alpha:
                    return beta
        return beta

    def action(self, turns):
        if self.board.count[self.mine] < 12:
            return self._place()
        return self._move(turns)

    def update(self, action):
        board = self.board
        if board.count[self.oppo] < 12:
            board.place(*action, self.oppo)
        else:
            src, dest = action
            board.move(*src, *dest)
