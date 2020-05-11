import math

from server.app import SimpleUncertainty


class Constants:
    def __init__(self, value, symbol=None):
        self.value = value
        self.symbol = symbol

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return self.value + other
        elif isinstance(other, Constants):
            return self.value + other.value
        elif isinstance(other, SimpleUncertainty):
            return SimpleUncertainty(self.value + other.value, other.uncertainty)

    def __radd__(self, other):
        if isinstance(other, (int, float)):
            return self.value + other
        elif isinstance(other, Constants):
            return self.value + other.value
        elif isinstance(other, SimpleUncertainty):
            return SimpleUncertainty(self.value + other.value, other.uncertainty)

    def __str__(self):
        return str(self.value)


pi = Constants(math.pi, 'π')
e = Constants(math.e, 'e')
R = Constants(8.31, 'R')

print(pi)
