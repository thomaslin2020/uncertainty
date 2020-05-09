import math
import numpy as np

from decimal import Decimal
from locale import atof
from server.scripts.standard import StdUncertainty
from server.scripts.simple import SimpleUncertainty


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


# note that the precision is limited by the maximum number of
# significant figures in the input
def round_to(o, n):
    max_sigfigs = len(atof(str(o.value), Decimal).as_tuple().digits)
    o.value = o.value if o.value < 1e-14 else o.value + 1e-15
    num = np.format_float_positional(o.value, precision=min(max_sigfigs, n), unique=False, fractional=False, trim='k')
    num = num[:-1] if num[-1] == '.' else num
    o.uncertainty = o.uncertainty if o.uncertainty < 1e-14 else o.uncertainty + 1e-15
    uncertainty = np.format_float_positional(o.uncertainty, precision=1, unique=False, fractional=False, trim='k')
    num_type = 'float' if '.' in num else 'int'
    if num_type == 'float':
        if (10 ** -(len(num[num.index('.'):]) - 1)) > float(uncertainty):
            uncertainty = '0'
        else:
            uncertainty_digits = 10 ** -math.floor(math.log10(float(uncertainty)))
            print(uncertainty_digits)
            num = round(float(num) * uncertainty_digits) / uncertainty_digits
            # num = "{:.{}f}".format(float(num), len(num[num.index('.'):]) - 1)
        return '(%s±%s)' % (num, uncertainty)
    else:
        if float(uncertainty) < 0.5:
            uncertainty = '0'
            return '(%s±%s)' % (num, uncertainty)
        else:
            uncertainty = round(float(uncertainty) if float(uncertainty) < 1e-14 else float(uncertainty) + 1e-15)
            uncertainty_digits = 10 ** math.floor(math.log10(uncertainty))
            uncertainty = '0' if uncertainty < 10 ** (len(str(num)) - n) else uncertainty
            num = int((int(num) // uncertainty_digits) * uncertainty_digits)
            return '(%s±%s)' % (str(num), uncertainty)


def r(o, n):  # shorthand for typing convenience
    return round_to(o, n)
