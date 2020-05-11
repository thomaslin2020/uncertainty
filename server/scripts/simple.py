from graphviz import Digraph


# level 0 = clustered operators, level 1 = normal computational graph (with all operators), level 2 = omit extra lines, level 3 = complete
# level -1 = omit all operators
class SimpleUncertainty:
    def __init__(self, value, uncertainty):
        self.value = value
        self.uncertainty = uncertainty

    def __neg__(self):
        return SimpleUncertainty(-self.value, self.uncertainty)

    def __abs__(self):
        return SimpleUncertainty(abs(self.value), self.uncertainty)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertainty(self.value + other, self.uncertainty)
        return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty)

    def __radd__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertainty(self.value + other, self.uncertainty)
        return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty)

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertainty(self.value - other, self.uncertainty)
        return SimpleUncertainty(self.value - other.value, self.uncertainty + other.uncertainty)

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertainty(other - self.value, self.uncertainty)
        return SimpleUncertainty(other.value - self.value, self.uncertainty + other.uncertainty)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertainty(self.value * other, self.uncertainty * other)
        temp = self.value * other.value
        return SimpleUncertainty(temp,
                                 abs(((self.uncertainty / abs(self.value)) + (
                                         other.uncertainty / abs(other.value))) * temp))

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertainty(self.value * other, self.uncertainty * other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertainty(self.value / other, self.uncertainty / other)
        temp = self.value / other.value
        return SimpleUncertainty(temp,
                                 abs(((self.uncertainty / abs(self.value)) + (
                                         other.uncertainty / abs(other.value))) * temp))

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertainty(other, 0) / SimpleUncertainty(self.value, self.uncertainty)

    def __pow__(self, power):
        temp = self.value ** power
        return SimpleUncertainty(temp, abs((self.uncertainty / abs(self.value)) * temp * power))

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)
