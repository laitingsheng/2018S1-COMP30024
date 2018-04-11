from abc import ABCMeta, abstractmethod

class Cell(metaclass=ABCMeta):
    __slots__ = ()

    def __eq__(self, o):
        if self is o:
            return True
        if isinstance(o, str):
            return self.sym == o
        return self.sym == o.sym

    def __ne__(self, o):
        return not self.__eq__(o)

    def __repr__(self):
        return self.sym

    def __str__(self):
        return self.sym

class Space(Cell):
    __slots__ = ()
    sym = '-'

class Block(Cell):
    __slots__ = ()
    sym = 'X'

class Piece(Cell, metaclass=ABCMeta):
    __slots__ = "num"

    def __eq__(self, o):
        if self is o:
            return True
        if isinstance(o, str):
            return self.sym == o
        return self.sym == o.sym and self.num == o.num

class White(Piece):
    __slots__ = ()
    opponent = '@'
    sym = 'O'

class Black(Piece):
    __slots__ = ()
    opponent = 'O'
    sym = '@'

class CellFactory:
    __slots__ = ()

    # avoid duplicate creations
    block = Block()
    space = Space()

    @classmethod
    def create(cls, name):
        if name == 'O':
            return White()
        if name == '@':
            return Black()
        if name == '-':
            return cls.space
        if name == 'X':
            return cls.block
        return None
