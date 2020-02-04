import random
import copy

from tools.lib import debug

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


    def copy(self):
        return copy.deepcopy(self)


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
        self.random_bound_restriction = 0.01


    def set_random_bound_restriction(self, val):
        self.random_bound_restriction = val
        return self


    def subdivision(self, b1):
        new = copy.deepcopy(self)
        new.br = Pos(new.tl.x + b1.br.x, new.tl.y + b1.br.y)
        new.tl.add(b1.tl)
        return new

    def center(self):
        return Pos(
            self.tl.x + (self.width / 2),
            self.tl.y + (self.height / 2)
        )


    def shift_y(self, amount):
        self.tl.y += amount
        self.br.y += amount
        return self


    def copy(self):
        return copy.deepcopy(self)


    def random_point(self):
        width_weight = self.width / 5
        height_weight = self.height / 5
        return Pos(
            random.randint(int(self.tl.x + width_weight), int(self.br.x - width_weight)),
            random.randint(int(self.tl.y + height_weight), int(self.br.y - height_weight))
        )