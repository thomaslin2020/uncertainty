import math


class StdUncertainty:
    def __init__(self, value, uncertainty):
        self.value = value
        self.uncertainty = uncertainty

    def __neg__(self):
        return StdUncertainty(-self.value, self.uncertainty)

    def __abs__(self):
        return StdUncertainty(abs(self.value), self.uncertainty)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertainty(self.value + other, self.uncertainty)
        return StdUncertainty(self.value + other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2))

    def __radd__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertainty(self.value + other, self.uncertainty)
        return StdUncertainty(self.value + other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2))

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertainty(self.value - other, self.uncertainty)
        return StdUncertainty(self.value - other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2))

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertainty(other - self.value, self.uncertainty)
        return StdUncertainty(self.value - other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2))

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertainty(self.value * other, self.uncertainty * other)
        temp = self.value * other.value
        return StdUncertainty(temp, abs(math.sqrt(
            ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp))

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertainty(self.value * other, self.uncertainty * other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertainty(self.value / other, self.uncertainty / other)
        temp = self.value / other.value
        return StdUncertainty(temp, abs(math.sqrt(
            ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp))

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertainty(other, 0) / StdUncertainty(self.value, self.uncertainty)

    def __pow__(self, power):
        temp = self.value ** power
        return StdUncertainty(temp, abs((self.uncertainty / abs(self.value)) * temp * power))

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)

    def __round__(self, n=None):
        pass
