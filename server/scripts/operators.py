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


def sanity_check(o, n):
    if o[-1] != '.' and o[0] == '0':  # if is in the form '0.#'
        temp = o[o.index('.') + 1:]
        contains_non_zero = False
        remove_non_zero = ''
        for i in temp:
            if i != '0':
                contains_non_zero = True
            if contains_non_zero:
                remove_non_zero += i
        if not contains_non_zero:  # does not contain non-zero
            return o
        else:
            o += '0' * (n - len(remove_non_zero))
            return o
    elif o[-1] != '.':  # if is in the form '#.#'
        return o + '0' * (n - (len(o) - 1))
    else:  # is integer
        return o


def integer_check(o, n):
    temp = o.replace('.', '')
    if len(o) == n and len(temp) > 1:
        if temp[-1] == '0':
            return o + '.'
    return o


# note that the precision is limited by the maximum number of
# significant figures in the input
# TODO: return a trigger when the number of sigfigs is capped
# note that the precision is limited by how python represents floats
# => numbers cannot end in a series of 0, must be followed by a non-zero number
# else 20.00 would be changed to 20.0
def round_to(o, n, cap_sigfigs):
    if cap_sigfigs == 0:
        cap_sigfigs = False
    if isinstance(o, (int, float)):
        max_sigfigs = 0
        if cap_sigfigs:
            max_sigfigs = len(atof(str(o), Decimal).as_tuple().digits)
            num = np.format_float_positional(o, precision=min(max_sigfigs, n),
                                             unique=False, fractional=False, trim='k')
            num = sanity_check(num, min(max_sigfigs, n))
        else:
            num = np.format_float_positional(o, precision=n,
                                             unique=False, fractional=False, trim='k')
            num = sanity_check(num, n)
        if num[-1] == '.':
            if cap_sigfigs:
                num = integer_check(num, min(max_sigfigs, n) + 1)
            else:
                num = integer_check(num, n + 1)
        num = num[:-1] if num[-1] == '.' else num
        return num

    temp = str(o.value)
    max_sigfigs = 0
    if cap_sigfigs:
        max_sigfigs = len(atof(str(o.value), Decimal).as_tuple().digits)
        o.value = o.value if o.value < 1e-14 else o.value + 1e-15
        num = np.format_float_positional(o.value, precision=min(max_sigfigs, n), unique=False, fractional=False,
                                         trim='k')
        num = sanity_check(num, min(max_sigfigs, n))
    else:
        o.value = o.value if o.value < 1e-14 else o.value + 1e-15
        num = np.format_float_positional(o.value, precision=n, unique=False, fractional=False,
                                         trim='k')
        num = sanity_check(num, n)
    num = num[:-1] if num[-1] == '.' else num
    o.uncertainty = o.uncertainty if o.uncertainty < 1e-14 else o.uncertainty + 1e-15
    uncertainty = np.format_float_positional(o.uncertainty, precision=1, unique=False, fractional=False, trim='k')
    num_type = 'float' if '.' in num else 'int'
    if num_type == 'float':
        ending = num[num.index('.') + 1:] if '.' in temp else ''
        if set(ending) == {'0'}:  # every number after decimal point is 0
            if uncertainty[-1] != '.':
                if len(ending) < len(uncertainty[uncertainty.index('.') + 1:]):
                    return '(%s±%s)' % (
                        num[:num.index('.') + len(uncertainty[uncertainty.index('.') + 1:]) + 1], '0')
            temp = uncertainty
            temp = temp[:-1] if temp[-1] == '.' else temp
            if uncertainty[-1] == '.':
                if cap_sigfigs:
                    num = np.format_float_positional(float(num), precision=min(max_sigfigs, n),
                                                     unique=False, fractional=False, trim='k')
                    num = sanity_check(num, min(max_sigfigs, n))
                else:
                    num = np.format_float_positional(float(num), precision=n,
                                                     unique=False, fractional=False, trim='k')
                    num = sanity_check(num, n)
                if num[-1] == '.':
                    if cap_sigfigs:
                        num = integer_check(num, min(max_sigfigs, n) + 1)
                    else:
                        num = integer_check(num, n + 1)
                num = num[:-1] if num[-1] == '.' else num
                return '(%s±%s)' % (num, temp)
            else:
                return '(%s±%s)' % (num[:num.index('.') + len(uncertainty[uncertainty.index('.') + 1:]) + 1], temp)

        # number is smaller than the smallest digit (unable to represent) - error is negligible
        elif 10 ** -(len(num[num.index('.'):]) - 1) > float(uncertainty):
            return '(%s±%s)' % (num, '0')
        else:
            uncertainty_digits = 10 ** -math.floor(math.log10(float(uncertainty)))
            num = str(round(float(temp) * uncertainty_digits) / uncertainty_digits)
            if cap_sigfigs:
                num = sanity_check(num, min(max_sigfigs, n))
            else:
                num = sanity_check(num, n)
            # print(num.index('.') + 1 + len(uncertainty[uncertainty.index('.') + 1:]))
            num = num[:num.index('.') + 1 + len(uncertainty[uncertainty.index('.') + 1:])]
            uncertainty = uncertainty[:-1] if uncertainty[-1] == '.' else uncertainty
            if not cap_sigfigs:
                num = np.format_float_positional(o.value, precision=n,
                                                 unique=False, fractional=False, trim='k')
                num = sanity_check(num, n)
            if num[-1] == '.':
                if cap_sigfigs:
                    num = integer_check(num, min(max_sigfigs, n) + 1)
                else:
                    num = integer_check(num, n + 1)
        return '(%s±%s)' % (num, uncertainty)
    else:
        if float(uncertainty) < 0.5:
            uncertainty = '0'
            if cap_sigfigs:
                return '(%s±%s)' % (integer_check(num, min(max_sigfigs, n)), uncertainty)
            else:
                return '(%s±%s)' % (integer_check(num, n), uncertainty)
        else:
            uncertainty = round(float(uncertainty) if float(uncertainty) < 1e-14 else float(uncertainty) + 1e-15)
            uncertainty_digits = 10 ** math.floor(math.log10(uncertainty))
            uncertainty = '0' if uncertainty < 10 ** (len(str(num)) - n) else uncertainty
            num = round(round(int(num) / uncertainty_digits) * uncertainty_digits)
            if cap_sigfigs:
                return '(%s±%s)' % (integer_check(str(num), min(max_sigfigs, n)), uncertainty)
            else:
                return '(%s±%s)' % (integer_check(str(num), n), uncertainty)


def r(o, n=3):  # shorthand for typing convenience
    return round_to(o, n, True)


def r_(o, n=3):  # shorthand for typing convenience
    return round_to(o, n, False)


# demo of difference between r_() and r()
"""
print(r(3.00, 5))
print(r_(3.00, 5))
print(r(SimpleUncertainty(3.000000, 0.00), 5))
print(r_(SimpleUncertainty(3.000000, 0.00), 5))
print(r_(SimpleUncertainty(0, 0), 5))
"""

# it should be noted that r() would omit trailing zeros
# if number is integer, trailing zeros would be omitted