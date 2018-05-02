import sys
from Player import Player
from Random import Player as RandomPlayer


def main():
    i = 1

    p = Player()
    rp = RandomPlayer()
    re = [0, 0, 50, 0, 0, 50]
    while re[2] + re[5] > 0:
        p.save(i)
        re = rp.test(p)
        print(re, file=sys.stderr)
        p.train(i)
        p.save(i)
        i += 1


if __name__ == "__main__":
    main()
