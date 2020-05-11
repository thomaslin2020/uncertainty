import math
from flask import Flask, request, jsonify
from flask_cors import CORS


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
                                 ((self.uncertainty / abs(self.value)) + (other.uncertainty / abs(other.value))) * temp)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertainty(self.value / other, self.uncertainty / other)
        temp = self.value / other.value
        return SimpleUncertainty(temp,
                                 ((self.uncertainty / abs(self.value)) + (other.uncertainty / abs(other.value))) * temp)

    def __pow__(self, power):
        temp = self.value ** power
        return SimpleUncertainty(temp, (self.uncertainty / abs(self.value)) * temp * power)

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)


class StdUncertainty:
    def __init__(self, value, uncertainty):
        self.value = value
        self.uncertainty = uncertainty

    def __neg__(self):
        return StdUncertainty(-self.value, self.uncertainty)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertainty(self.value + other, self.uncertainty)
        return StdUncertainty(self.value + other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2))

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertainty(self.value - other, self.uncertainty)
        return StdUncertainty(self.value - other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2))

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertainty(self.value * other, self.uncertainty * other)
        temp = self.value * other.value
        return StdUncertainty(temp, math.sqrt(
            ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertainty(self.value / other, self.uncertainty / other)
        temp = self.value / other.value
        return StdUncertainty(temp, math.sqrt(
            ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp)

    def __pow__(self, power):
        temp = self.value ** power
        return StdUncertainty(temp, (self.uncertainty / abs(self.value)) * temp * power)

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)


def sin(o):
    value = math.sin(o.value)
    uncertainty = math.cos(o.value) * o.uncertainty
    return SimpleUncertainty(value, abs(uncertainty)) \
        if isinstance(o, SimpleUncertainty) else StdUncertainty(value, abs(uncertainty))


def cos(o):
    value = math.cos(o.value)
    uncertainty = math.sin(o.value) * o.uncertainty
    return SimpleUncertainty(value, abs(uncertainty)) \
        if isinstance(o, SimpleUncertainty) else StdUncertainty(value, abs(uncertainty))


def tan(o):
    value = math.tan(o.value)
    uncertainty = o.uncertainty / (math.cos(o.value) ** 2)
    return SimpleUncertainty(value, abs(uncertainty)) \
        if isinstance(o, SimpleUncertainty) else StdUncertainty(value, abs(uncertainty))


def arcsin(o):
    value = math.asin(o.value)
    uncertainty = o.uncertainty / math.sqrt(1 - o.value ** 2)
    return SimpleUncertainty(value, abs(uncertainty)) \
        if isinstance(o, SimpleUncertainty) else StdUncertainty(value, abs(uncertainty))


def arccos(o):
    value = math.acos(o.value)
    uncertainty = -o.uncertainty / math.sqrt(1 - o.value ** 2)
    return SimpleUncertainty(value, abs(uncertainty)) \
        if isinstance(o, SimpleUncertainty) else StdUncertainty(value, abs(uncertainty))


def arctan(o):
    value = math.atan(o.value)
    uncertainty = o.uncertainty / (1 + o.value ** 2)
    return SimpleUncertainty(value, abs(uncertainty)) \
        if isinstance(o, SimpleUncertainty) else StdUncertainty(value, abs(uncertainty))


def exp(o):
    value = math.exp(o.value)
    uncertainty = math.exp(o.value) * o.uncertainty
    return SimpleUncertainty(value, abs(uncertainty)) \
        if isinstance(o, SimpleUncertainty) else StdUncertainty(value, abs(uncertainty))


def log(o, base=10):
    value = math.log(o.value, base)
    uncertainty = o.uncertainty / (math.log(base, math.e) * o.value)
    return SimpleUncertainty(value, abs(uncertainty)) \
        if isinstance(o, SimpleUncertainty) else StdUncertainty(value, abs(uncertainty))


def ln(o):
    value = math.log(o.value, math.e)
    uncertainty = o.uncertainty / o.value
    return SimpleUncertainty(value, abs(uncertainty)) \
        if isinstance(o, SimpleUncertainty) else StdUncertainty(value, abs(uncertainty))


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(DEBUG=False)
CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return 'Hello World'
    if request.method == 'POST':
        U = None
        if request.form['method'] == 'simple':
            U = SimpleUncertainty
        else:
            U = StdUncertainty
        try:
            return str(eval(request.form['equation']))
        except:
            return 'Please fix your equation'


if __name__ == '__main__':
    app.run(port='5002')
