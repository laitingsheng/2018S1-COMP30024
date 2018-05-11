import math

from Board import Board


inf = float("inf")
cm2 = cm3 = cp2 = cp3 = 0.5
cp1 = cm1 = 3
cp4 = cp5 = cm4 = cm5 = 2


class Player:
    __slots__ = "board", "depth", "mine", "oppo"

    def __init__(self, colour, depth=4):
        if colour == "white":
            self.mine = 0
            self.oppo = 1
        else:
            self.mine = 1
            self.oppo = 0

        self.board = Board()
        self.depth = 1 if depth < 1 else depth

    def _eval_move(self, board):
        if board.n_pieces[self.oppo] < 2:
            return inf

        re = cm1 * (board.n_pieces[self.mine] - board.n_pieces[self.oppo])
        re *= max(board.n_pieces[self.mine], board.n_pieces[self.oppo]) + 1
        re /= min(board.n_pieces[self.mine], board.n_pieces[self.oppo]) + 1

        for x, y in filter(None, board.pieces[self.mine]):
            re -= cm2 * (abs(x - 3.5) + abs(y - 3.5))
            psur = board.potential_surrounded(x, y)
            used_pieces = psur[1]
            psurrpoint = psur[2]
            for i in range(len(used_pieces)):
                if self._reachable(
                    board, self.oppo, psurrpoint[i][0], psurrpoint[i][1],
                    used_pieces[i]
                ):
                    re -= cm4

        for x, y in filter(None, board.pieces[self.oppo]):
            re += cm3 * (abs(x - 3.5) + abs(y - 3.5))
            psur = board.potential_surrounded(x, y)
            used_pieces = psur[1]
            psurrpoint = psur[2]
            for i in range(len(used_pieces)):
                if self._reachable(
                    board, self.mine, psurrpoint[i][0], psurrpoint[i][1],
                    used_pieces[i]
                ):
                    re += cm5

        return re

    def _eval_place(self, board):

        re = cp1 * (board.n_pieces[self.mine] - board.n_pieces[self.oppo])
        re *= max(board.n_pieces[self.mine], board.n_pieces[self.oppo]) + 1
        re /= min(board.n_pieces[self.mine], board.n_pieces[self.oppo]) + 1

        for x, y in filter(None, board.pieces[self.mine]):
            re -= cp2 * (abs(x - 3.5) + abs(y - 3.5))
            for psx, psy in board.potential_surrounded(x, y)[2]:
                if (self.oppo == 0 and psy < 6) or \
                   (self.oppo == 1 and psy > 1):
                        re -= cp4

        for x, y in filter(None, board.pieces[self.oppo]):
            re += cp3 * (abs(x - 3.5) + abs(y - 3.5))
            for psx, psy in board.potential_surrounded(x, y)[2]:
                if (self.mine == 0 and psy < 6) or \
                   (self.mine == 1 and psy > 1):
                        re += cp5

        return re

    def _move(self, turns):
        board = self.board
        alpha = -inf
        s = None
        mine = self.mine
        for src, dests in board.valid_move(mine):
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
            return self._eval_move(board)

        depth += 1
        turns += 1
        updated = False
        mine = self.mine
        for src, dests in board.valid_move(mine):
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
            return self._eval_move(board)

        depth += 1
        turns += 1
        updated = False
        oppo = self.oppo
        for src, dests in board.valid_move(oppo):
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
        mine = self.mine
        alpha = -inf
        for pos in board.valid_place(mine):
            b = board.copy()
            b.place(*pos, mine)
            re = self._place_min(b, 1, alpha, inf)
            if re > alpha:
                alpha = re
                p = pos
        board.place(*p, mine)
        return p

    def _place_max(self, board, depth, alpha, beta):
        mine = self.mine
        if board.count[mine] == 12:
            return self._move_max(board, depth, 0, alpha, beta)

        if depth == self.depth:
            return self._eval_place(board)

        depth += 1
        for pos in board.valid_place(mine):
            b = board.copy()
            b.place(*pos, mine)
            re = self._place_min(b, depth, alpha, beta)
            if re > alpha:
                alpha = re
                if alpha >= beta:
                    return beta
        return alpha

    def _place_min(self, board, depth, alpha, beta):
        oppo = self.oppo
        if board.count[oppo] == 12:
            return self._move_min(board, depth, 0, alpha, beta)

        if depth == self.depth:
            return self._eval_place(board)

        depth += 1
        for pos in board.valid_place(oppo):
            b = board.copy()
            b.place(*pos, oppo)
            re = self._place_max(b, depth, alpha, beta)
            if re < beta:
                beta = re
                if beta <= alpha:
                    return beta
        return beta

    def _reachable(self, board, player, x, y, used_piece):
        for dx, dy in ((1, 0), (0, 1), (0, -1), (-1, 0)):
            nx, ny = x + dx, y + dy
            if board._inboard(nx, ny):
                p = board.board[ny][nx]
                if p // 0x10 == player:
                    return True
            nx, ny = nx + dx, ny + dy
            if board._inboard(nx, ny):
                np = board.board[ny][nx]
                if ((p // 0x10 == player) or (p // 0x10 == 1 - player)) and \
                   np != used_piece and np // 0x10 == player:
                    return True
        return False

    def action(self, turns):
        if self.board.count[self.mine] < 12:
            return self._place()
        return self._move(turns)

    def update(self, action):
        board = self.board
        if board.count[self.oppo] < 12:
            board.place(*action, self.oppo)
        elif action is None:
            self.board.forfeit()
        else:
            src, dest = action
            board.move(*src, *dest)
