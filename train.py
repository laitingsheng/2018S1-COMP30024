import sys
from Player import Player
from Random import Player as RandomPlayer


def main():
    i = 1

    p = Player(load=True)
    rp = RandomPlayer()

    print('-' * 8 + "initialise" + '-' * 8, file=sys.stderr)
    bre = pre = rp.test(p)
    print(pre, file=sys.stderr)

    while pre[0] + pre[3] < 100:
        p.train(i)
        p.save()

        re = rp.test(p)
        print(re, file=sys.stderr)

        if re[0] + re[3] > bre[0] + bre[3]:
            print("find a better model", file=sys.stderr)
            p.save("best")
            bre = re

        i += 1
        pre = re


if __name__ == "__main__":
    main()
