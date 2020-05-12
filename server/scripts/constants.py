import math

from server.app import SimpleUncertainty


class Constants:
    def __init__(self, value, symbol=None, description=None):
        self.value = value
        self.symbol = symbol
        self.description = description

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
R = Constants(8.314462618, 'R', 'gas constant')
tau = Constants(math.tau, 'τ')
g = Constants(9.80665, 'g', 'acceleration of free fall (earth\'s surface)')
G = Constants(6.67430 * (10 ** -11), 'G', 'gravitational constant')
c = Constants(299792458, 'c', 'speed of light')
giga = Constants(10 ** 9, 'G')
mega = Constants(10 ** 6, 'M')
kilo = Constants(10 ** 3, 'k')
hecto = Constants(10 ** 2, 'h')
deca = Constants(10 ** 1, 'da')
deci = Constants(10 ** -1, 'd')
centi = Constants(10 ** -2, 'c')
milli = Constants(10 ** -3, 'm')
micro = Constants(10 ** -6, 'μ')
nano = Constants(10 ** -9, 'n')
ly = Constants(9.46e15, 'ly')
atm = Constants(101325, 'atm')
