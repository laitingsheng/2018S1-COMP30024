import sys
from Player import Player
from Random import Player as RandomPlayer


def main():
    i = 1

    p = Player(load=True)
    rp = RandomPlayer()
    pre = [0, 0, 100, 0, 0, 100]
    bre = [0] * 6
    while pre[2] + pre[5] > 0 or pre[0] + pre[3] < 190:
        p.save(i)
        p.train(i)
        p.save(i)

        re = rp.test(p)
        print(re, file=sys.stderr)

        if re[0] + re[3] > bre[0] + bre[3]:
            print("find a better model", file=sys.stderr)
            p.save(i, "best")
            bre = re

        i += 1
        pre = re


if __name__ == "__main__":
    main()
