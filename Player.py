from Board import Board


class Player:
    __slots__ = "board", "depth", "mine", "oppo", "turn_step", "turn_thres"

    def __init__(self, colour, depth=20):
        if colour == 'O':
            self.mine = 0x0
            self.oppo = 0x10
        else:
            self.mine = 0x10
            self.oppo = 0x0

        self.board = Board()
        self.depth = depth
        self.turn_thres = self.turn_step = 128

    def _move(self, turns):
        src, dest = self._move_search(self.depth, turns)
        self.board.move(*src, *dest)
        return (src, dest)

    def _move_search(self, depth, turns):
        pass

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
