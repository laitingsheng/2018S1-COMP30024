from Board import Board
# import __lt__ and __gt__ instead of lt and gt to avoid naming conflict
from operator import __lt__, __gt__


class Player:
    __slots__ = "board", "depth", "mine", "oppo", "turn_step", "turn_thres"
    cmps = None, __gt__, __lt__

    def __init__(self, colour, depth=3):
        if colour == 'O':
            self.mine = 0x0
            self.oppo = 0x10
        else:
            self.mine = 0x10
            self.oppo = 0x0
        self.types = None, self.mine // 0x10, self.oppo // 0x10

        self.board = Board()
        self.depth = depth
        self.turn_thres = self.turn_step = 128

    def _benchmark(self, board, turns):
        pass

    def _move(self, turns):
        board = self.board
        score = -inf
        turns += 1
        for src, dests in board.valid_move(self.mine // 0x10):
            for dest in dests:
                b = board.copy()
                b.move(*src, *dest)
                re = self._move_search(b, 1, turns, score, 1)
                if re > score:
                    score = re
                    s, d = src, dest

        self.board.move(*s, *d)
        return (s, d)

    def _move_search(self, board, depth, turns, parent_score, parent_sign):
        if depth == self.depth:
            return self._benchmark(board, turns)

        parent_cmp = self.cmps[parent_sign]
        sign = -parent_sign
        cmp = self.cmps[sign]
        type = self.types[sign]
        score = inf if sign < 0 else -inf

        depth += 1
        turns += 1
        for src, dests in board.valid_move(type):
            for dest in dests:
                b = board.copy()
                b.move(*src, *dest)
                re = self._move_search(b, depth, turns, score, sign)

                # two circumstances
                # * current is a min node, then
                #   1. child score < current score, update the score
                #   2. if updated score not greater than the parent score,
                #      simply return current score (beta)
                # * current is a max node, then
                #   1. child score > current score, update the score
                #   2. if updated score not smaller than the parent score,
                #      simply return current score (alpha)
                if cmp(re, score):
                    score = re
                    if not parent_cmp(score, parent_score):
                        return score
        return score

    def _place(self):
        pos = self._place_search(self.depth)
        self.board.place(*pos, self.mine)
        self.mine += 1
        return pos

    def _place_search(self, depth):
        pass

    def action(self, turns):
        if self.mine < 12:
            return self._place()

        if turns > self.turn_thres:
            self.turn_step //= 2
            self.turn_thres += self.turn_step
            self.board.shrink()
        return self._move(turns)

    def update(self, action):
        if self.mine < 12:
            self.board.place(*action, self.oppo)
            self.oppo += 1
        else:
            src, dest = action
            self.board.move(*src, *dest)
