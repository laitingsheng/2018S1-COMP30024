import numpy as np
from collections import Counter

from Board import Board
from referee import _Game, _InvalidActionException


class Player:
    def __init__(self, colour=None, board=None):
        if board is None:
            self.board = Board()
        else:
            self.board = board

    def _move(self):
        vm = self.board.valid_move
        if vm.sum() < 1:
            return self.board.forfeit_move()
        return self.board.interpret_move(
            np.random.choice(512, p=vm / vm.sum())
        )

    def _place(self):
        vp = self.board.valid_place
        return self.board.interpret_place(
            np.random.choice(48, p=vp / vp.sum())
        )

    def action(self, turns):
        if self.board.placing:
            return self._place()
        return self._move()

    def test(self, other):
        w_counter = Counter()
        print("White test")
        for i in range(50):
            game = _Game()
            self.board.__init__()
            other.board.__init__()
            mine, oppo = other, self
            print(f"Game {i} started")
            print(game)
            while game.playing():
                turns = game.turns
                action = mine.action(turns)
                try:
                    game.update(action)
                except _InvalidActionException as e:
                    print(f"invalid action ({game.loser}):", e)
                    raise RuntimeError()
                print(game)
                oppo.update(action)
                mine, oppo = oppo, mine
            if game.winner == 'B':
                reward = -1
            elif game.winner == 'W':
                reward = 1
            else:
                reward = 0
            w_counter.update([reward])

        b_counter = Counter()
        print("Black test")
        for i in range(50):
            game = _Game()
            self.board.__init__()
            other.board.__init__()
            mine, oppo = self, other
            print(f"Game {i} started")
            print(game)
            while game.playing():
                turns = game.turns
                action = mine.action(turns)
                try:
                    game.update(action)
                except _InvalidActionException as e:
                    print(f"invalid action ({game.loser}):", e)
                    raise RuntimeError()
                print(game)
                oppo.update(action)
                mine, oppo = oppo, mine
            if game.winner == 'W':
                reward = -1
            elif game.winner == 'B':
                reward = 1
            else:
                reward = 0
            b_counter.update([reward])

        results = [w_counter[1], w_counter[0], w_counter[-1],
                   b_counter[1], b_counter[0], b_counter[-1]]

        return results

    def update(self, action):
        if self.board.placing:
            self.board.place(*action)
        elif action is None:
            self.board.forfeit_move()
        else:
            src, dest = action
            self.board.move(*src, *dest)
