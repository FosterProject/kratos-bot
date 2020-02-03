import random

class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y


    def scale(self, factor):
        self.x = self.x * factor
        self.y = self.y * factor
        return self


    def to_int(self):
        self.x = int(self.x)
        self.y = int(self.y)
        return self


    def add(self, p1):
        self.x += p1.x
        self.y += p1.y
        return self


    def subtract(self, p1):
        self.x -= p1.x
        self.y -= p1.y
        return self


    def add_raw(self, x1, y1):
        self.x += x1
        self.y += y1
        return self


    def __str__(self):
        return "Point(x: %s, y: %s)" % (self.x, self.y)

    @staticmethod
    def random(topleft, bottomright):
        return Pos(
            random.randint(topleft.x, bottomright.x),
            random.randint(topleft.y, bottomright.y)
        )


class Box:
    def __init__(self, tl, br):
        self.tl = tl
        self.br = br
        self.width = br.x - tl.x
        self.height = br.y - tl.y


    def subdivision(self, b1):
        tmp = self.tl
        self.tl.add(b1.tl)
        self.br = tmp.add(b1.br)
        return self

    def center(self):
        return Pos(
            self.tl.x + (self.width / 2),
            self.tl.y + (self.height / 2)
        )


    def random_point(self):
        return Pos(
            random.randint(self.tl.x, self.br.x),
            random.randint(self.tl.y, self.br.y)
        )