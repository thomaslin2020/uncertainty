import math

from server.standard import StdUncertainty
from server.simple import SimpleUncertainty


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
