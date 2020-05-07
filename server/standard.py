import math


class StdUncertainty:
    def __init__(self, a, b):
        self.value = a
        self.uncertainty = b

    def __neg__(self):
        return StdUncertainty(-self.value, self.uncertainty)

    def __add__(self, other):
        return StdUncertainty(self.value + other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2))

    def __sub__(self, other):
        return StdUncertainty(self.value - other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2))

    def __mul__(self, other):
        temp = self.value * other.value
        return StdUncertainty(temp, math.sqrt(
            ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp)

    def __truediv__(self, other):
        temp = self.value / other.value
        return StdUncertainty(temp, math.sqrt(
            ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp)

    def __pow__(self, power):
        temp = self.value ** power
        return StdUncertainty(temp, (self.uncertainty / abs(self.value)) * temp * power)

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)
