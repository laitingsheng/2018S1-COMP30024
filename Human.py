class Player:
    __slots__ = "placing"

    def __init__(self, colour):
        self.placing = True
        print(f"Colour: {colour}")

    def action(self, turns):
        print(f"Turn {turns}:")
        if self.placing:
            x, y = input().split()
            if turns in (22, 23):
                self.placing = False
            return int(x), int(y)
        sx, sy, dx, dy = input().split()
        return (int(sx), int(sy)), (int(dx), int(dy))

    def update(self, action):
        print(action)
