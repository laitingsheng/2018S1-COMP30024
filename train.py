from Player import Player


def main():
    i = 1

    p = Player()
    while True:
        print(i)
        p.train(i)
        p.save(i)
        i += 1


if __name__ == "__main__":
    main()
