class SimpleUncertainty:
    def __init__(self, value, uncertainty):
        self.value = value
        self.uncertainty = uncertainty

    def __neg__(self):
        return SimpleUncertainty(-self.value, self.uncertainty)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertainty(self.value + other, self.uncertainty)
        return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty)

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertainty(self.value - other, self.uncertainty)
        return SimpleUncertainty(self.value - other.value, self.uncertainty + other.uncertainty)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertainty(self.value * other, self.uncertainty * other)
        temp = self.value * other.value
        return SimpleUncertainty(temp,
                                 abs(((self.uncertainty / abs(self.value)) + (
                                         other.uncertainty / abs(other.value))) * temp))

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertainty(self.value / other, self.uncertainty / other)
        temp = self.value / other.value
        return SimpleUncertainty(temp,
                                 abs(((self.uncertainty / abs(self.value)) + (
                                             other.uncertainty / abs(other.value))) * temp))

    def __pow__(self, power):
        temp = self.value ** power
        return SimpleUncertainty(temp, abs((self.uncertainty / abs(self.value)) * temp * power))

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)
