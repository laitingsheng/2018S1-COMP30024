import sys
from Player import Player
from Random import Player as RandomPlayer


def main():
    i = 1

    p = Player()
    rp = RandomPlayer()
    pre = [0, 0, 50, 0, 0, 50]
    while pre[2] + pre[5] > 0 or pre[0] + pre[3] < 190:
        # train and save the weights
        p.train(i)
        p.save(i)

        re = rp.test(p)
        print(re, file=sys.stderr)

        if re[0] + re[3] > pre[0] + pre[3]:
            print("find a better model", file=sys.stderr)
            p.save(i, "best")

        i += 1
        re = pre


if __name__ == "__main__":
    main()
