import math
import sys

from graphviz import Digraph


def start_session(f='pdf'):
    n = iter(range(sys.maxsize))
    d = Digraph(strict=False, format=f)
    return n, d


num, dot = start_session()


def unary_temp_node_full(o, name, value, uncertainty):
    node = str(next(num))
    dot.node(node, name)
    dot.edge(o.node, node)
    t1, t2 = str(next(num)), str(next(num))
    dot.node(t1, value)
    dot.node(t2, uncertainty)
    dot.edge(node, t1, xlabel=' Value ')
    dot.edge(node, t2, label=' Uncertainty ')
    return t1, t2


def temp_node_full(o):
    temp = str(next(num))
    dot.node(temp, '%.3g' % o)
    return temp


def binary_node_full(s, o, operator, value_calculation, uncertainty_calculation):
    operator_node = str(next(num))
    dot.node(operator_node, operator)
    dot.edge(s.node, operator_node)
    dot.edge(o, operator_node)
    t1, t2 = str(next(num)), str(next(num))
    dot.node(t1, value_calculation)
    dot.node(t2, uncertainty_calculation)
    dot.edge(operator_node, t1, xlabel=' Value ')
    dot.edge(operator_node, t2, label=' Uncertainty ')
    return t1, t2


class SimpleUncertaintyFull:  # normal
    def __init__(self, value, uncertainty, *nodes, symbol=None):
        self.value = value
        self.uncertainty = uncertainty
        self.nodes = nodes
        self.symbol = symbol
        self.node = str(next(num))
        dot.node(self.node, symbol) if symbol else dot.node(self.node,
                                                            '(%.3g±%.3g)' % (self.value, self.uncertainty))
        dot.edges([(n, self.node) for n in self.nodes])

    def __neg__(self):
        operator = 'neg'
        operator_node = str(next(num))
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        t1, t2 = str(next(num)), str(next(num))
        dot.node(t1, "%.3g" % -self.value)
        dot.node(t2, "%.3g" % self.uncertainty)
        dot.edge(operator_node, t1, xlabel=' Value ')
        dot.edge(operator_node, t2, label=' Uncertainty ')
        return SimpleUncertaintyFull(-self.value, self.uncertainty, t1, t2)

    def __abs__(self):
        operator = 'abs'
        operator_node = str(next(num))
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        t1, t2 = str(next(num)), str(next(num))
        dot.node(t1, "%.3g" % abs(self.value))
        dot.node(t2, "%.3g" % self.uncertainty)
        dot.edge(operator_node, t1, xlabel=' Value ')
        dot.edge(operator_node, t2, label=' Uncertainty ')
        return SimpleUncertaintyFull(abs(self.value), self.uncertainty, t1, t2)

    def __add__(self, other):
        operator = '+'
        if isinstance(other, (int, float)):
            temp = temp_node_full(other)
            return SimpleUncertaintyFull(self.value + other, self.uncertainty,
                                         *binary_node_full(self, temp, operator, '%.3g + %.3g' % (self.value, other),
                                                           'Δ: %.3g + 0' % self.uncertainty))
        return SimpleUncertaintyFull(self.value + other.value, self.uncertainty + other.uncertainty,
                                     *binary_node_full(self, other.node, operator,
                                                       '%.3g + %.3g' % (self.value, other.value),
                                                       'Δ: %.3g + %.3g' % (self.uncertainty, other.uncertainty)))

    def __radd__(self, other):
        operator = '+'
        temp = temp_node_full(other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        return SimpleUncertaintyFull(self.value + other, self.uncertainty,
                                     *binary_node_full(self, temp, operator, '%.3g + %.3g' % (other, self.value),
                                                       'Δ: 0 + %.3g' % self.uncertainty))

    def __sub__(self, other):
        operator = '-'
        if isinstance(other, (int, float)):
            temp = temp_node_full(other)
            return SimpleUncertaintyFull(self.value - other, self.uncertainty,
                                         *binary_node_full(self, temp, operator, '%.3g - %.3g' % (self.value, other),
                                                           'Δ: %.3g + 0' % self.uncertainty))
        return SimpleUncertaintyFull(self.value - other.value, self.uncertainty + other.uncertainty,
                                     *binary_node_full(self, other.node, operator,
                                                       '%.3g - %.3g' % (self.value, other.value),
                                                       'Δ: %.3g + %.3g' % (self.uncertainty, other.uncertainty)))

    def __rsub__(self, other):
        operator = '-'
        temp = temp_node_full(other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        return SimpleUncertaintyFull(other - self.value, self.uncertainty,
                                     *binary_node_full(self, temp, operator, '%.3g - %.3g' % (other, self.value),
                                                       'Δ: 0 + %.3g' % self.uncertainty))

    def __mul__(self, other):
        operator = '⨉'
        if isinstance(other, (int, float)):
            temp = temp_node_full(other)
            return SimpleUncertaintyFull(self.value * other, self.uncertainty * other,
                                         *binary_node_full(self, temp, operator, '%.3g ⨉ %.3g' % (self.value, other),
                                                           'Δ: %.3g ⨉ %.3g' % (self.uncertainty, other)))
        temp = self.value * other.value
        return SimpleUncertaintyFull(temp, abs(((self.uncertainty / abs(self.value)) + (
                other.uncertainty / abs(other.value))) * temp),
                                     *binary_node_full(self, other.node, operator,
                                                       '%.3g ⨉ %.3g' % (self.value, other.value),
                                                       'Δ: [(%.3g/%.3g)+(%.3g/%.3g)] ⨉ %.3g' % (
                                                           self.uncertainty, self.value, other.uncertainty, other.value,
                                                           temp)))

    def __rmul__(self, other):
        operator = '⨉'
        temp = temp_node_full(other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        return SimpleUncertaintyFull(self.value * other, self.uncertainty * other,
                                     *binary_node_full(self, temp, operator, '%.3g ⨉ %.3g' % (other, self.value),
                                                       'Δ: %.3g ⨉ %.3g' % (other, self.uncertainty)))

    def __truediv__(self, other):
        operator = '÷'
        if isinstance(other, (int, float)):
            temp = temp_node_full(other)
            return SimpleUncertaintyFull(self.value / other, self.uncertainty / other,
                                         *binary_node_full(self, temp, operator, '%.3g / %.3g' % (self.value, other),
                                                           'Δ: %.3g / %.3g' % (self.uncertainty, other)))
        temp = self.value / other.value
        return SimpleUncertaintyFull(temp, abs(((self.uncertainty / abs(self.value)) + (
                other.uncertainty / abs(other.value))) * temp),
                                     *binary_node_full(self, other.node, operator,
                                                       '%.3g / %.3g' % (self.value, other.value),
                                                       'Δ: [(%.3g/%.3g)+(%.3g/%.3g)] ⨉ %.3g' % (
                                                           self.uncertainty, self.value, other.uncertainty, other.value,
                                                           temp)))

    def __rtruediv__(self, other):
        operator = '÷'
        temp = temp_node_full(other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        temp_value = other / self.value
        return SimpleUncertaintyFull(temp_value, temp_value * self.uncertainty / self.value,
                                     *binary_node_full(self, temp, operator, '%.3g / %.3g' % (other, self.value),
                                                       'Δ: %.3g / %.3g' % (other, self.uncertainty)))

    def __pow__(self, power):
        operator = '^'
        operator_node = str(next(num))
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        t1, t2 = str(next(num)), str(next(num))
        temp = self.value ** power
        dot.node(t1, "%.3g ^ %.3g" % (self.value, power))
        dot.node(t2, "(%.3g/%.3g) ⨉ (%.3g^%.3g) ⨉ %.3g" % (self.uncertainty, self.value, self.value, power, power))
        dot.edge(operator_node, t1, xlabel=' Value ')
        dot.edge(operator_node, t2, label=' Uncertainty ')
        return SimpleUncertaintyFull(temp, abs((self.uncertainty / abs(self.value)) * temp * power), t1, t2)

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)


class StdUncertaintyFull:  # normal
    def __init__(self, value, uncertainty, *nodes, symbol=None):
        self.value = value
        self.uncertainty = uncertainty
        self.nodes = nodes
        self.symbol = symbol
        self.node = str(next(num))
        dot.node(self.node, symbol) if symbol else dot.node(self.node,
                                                            '(%.3g±%.3g)' % (self.value, self.uncertainty))
        dot.edges([(n, self.node) for n in self.nodes])

    def __neg__(self):
        operator = 'neg'
        operator_node = str(next(num))
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        t1, t2 = str(next(num)), str(next(num))
        dot.node(t1, "%.3g" % -self.value)
        dot.node(t2, "%.3g" % self.uncertainty)
        dot.edge(operator_node, t1, xlabel=' Value ')
        dot.edge(operator_node, t2, label=' Uncertainty ')
        return StdUncertaintyFull(-self.value, self.uncertainty, t1, t2)

    def __abs__(self):
        operator = 'abs'
        operator_node = str(next(num))
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        t1, t2 = str(next(num)), str(next(num))
        dot.node(t1, "%.3g" % abs(self.value))
        dot.node(t2, "%.3g" % self.uncertainty)
        dot.edge(operator_node, t1, xlabel=' Value ')
        dot.edge(operator_node, t2, label=' Uncertainty ')
        return StdUncertaintyFull(abs(self.value), self.uncertainty, t1, t2)

    def __add__(self, other):
        operator = '+'
        if isinstance(other, (int, float)):
            temp = temp_node_full(other)
            return StdUncertaintyFull(self.value + other, self.uncertainty,
                                      *binary_node_full(self, temp, operator, '%.3g + %.3g' % (self.value, other),
                                                        'Δ: %.3g + 0' % self.uncertainty))
        return StdUncertaintyFull(self.value + other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2),
                                  *binary_node_full(self, other.node, operator,
                                                    '%.3g + %.3g' % (self.value, other.value),
                                                    'Δ: sqrt(%.3g⋅%.3g + %.3g⋅%.3g)' % (
                                                        self.uncertainty, self.uncertainty, other.uncertainty,
                                                        other.uncertainty)))

    def __radd__(self, other):
        operator = '+'
        temp = temp_node_full(other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        return StdUncertaintyFull(self.value + other, self.uncertainty,
                                  *binary_node_full(self, temp, operator, '%.3g + %.3g' % (other, self.value),
                                                    'Δ: 0 + %.3g' % self.uncertainty))

    def __sub__(self, other):
        operator = '-'
        if isinstance(other, (int, float)):
            temp = temp_node_full(other)
            return StdUncertaintyFull(self.value - other, self.uncertainty,
                                      *binary_node_full(self, temp, operator, '%.3g - %.3g' % (self.value, other),
                                                        'Δ: %.3g + 0' % self.uncertainty))
        return StdUncertaintyFull(self.value - other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2),
                                  *binary_node_full(self, other.node, operator,
                                                    '%.3g - %.3g' % (self.value, other.value),
                                                    'Δ: sqrt(%.3g⋅%.3g + %.3g⋅%.3g)' % (
                                                        self.uncertainty, self.uncertainty, other.uncertainty,
                                                        other.uncertainty)))

    def __rsub__(self, other):
        operator = '-'
        temp = temp_node_full(other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        return StdUncertaintyFull(other - self.value, self.uncertainty,
                                  *binary_node_full(self, temp, operator, '%.3g - %.3g' % (other, self.value),
                                                    'Δ: 0 + %.3g' % self.uncertainty))

    def __mul__(self, other):
        operator = '⨉'
        if isinstance(other, (int, float)):
            temp = temp_node_full(other)
            return StdUncertaintyFull(self.value * other, self.uncertainty * other,
                                      *binary_node_full(self, temp, operator, '%.3g ⨉ %.3g' % (self.value, other),
                                                        'Δ: %.3g ⨉ %.3g' % (self.uncertainty, other)))
        temp = self.value * other.value
        return StdUncertaintyFull(temp, abs(math.sqrt(
            ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp),
                                  *binary_node_full(self, other.node, operator,
                                                    '%.3g ⨉ %.3g' % (self.value, other.value),
                                                    'Δ: sqrt[(%.3g/%.3g)^2+(%.3g/%.3g)^2] ⨉ %.3g' % (
                                                        self.uncertainty, self.value, other.uncertainty, other.value,
                                                        temp)))

    def __rmul__(self, other):
        operator = '⨉'
        temp = temp_node_full(other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        return StdUncertaintyFull(self.value * other, self.uncertainty * other,
                                  *binary_node_full(self, temp, operator, '%.3g ⨉ %.3g' % (other, self.value),
                                                    'Δ: %.3g ⨉ %.3g' % (other, self.uncertainty)))

    def __truediv__(self, other):
        operator = '÷'
        if isinstance(other, (int, float)):
            temp = temp_node_full(other)
            return StdUncertaintyFull(self.value / other, self.uncertainty / other,
                                      *binary_node_full(self, temp, operator, '%.3g / %.3g' % (self.value, other),
                                                        'Δ: %.3g / %.3g' % (self.uncertainty, other)))
        temp = self.value / other.value
        return StdUncertaintyFull(temp, abs(math.sqrt(
            ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp),
                                  *binary_node_full(self, other.node, operator,
                                                    '%.3g / %.3g' % (self.value, other.value),
                                                    'Δ: sqrt[(%.3g/%.3g)^2+(%.3g/%.3g)^2] ⨉ %.3g' % (
                                                        self.uncertainty, self.value, other.uncertainty, other.value,
                                                        temp)))

    def __rtruediv__(self, other):
        operator = '÷'
        temp = temp_node_full(other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        temp_value = other / self.value
        return StdUncertaintyFull(temp_value, temp_value * self.uncertainty / self.value,
                                  *binary_node_full(self, temp, operator, '%.3g / %.3g' % (other, self.value),
                                                    'Δ: %.3g / %.3g' % (other, self.uncertainty)))

    def __pow__(self, power):
        operator = '^'
        operator_node = str(next(num))
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        t1, t2 = str(next(num)), str(next(num))
        temp = self.value ** power
        dot.node(t1, "%.3g ^ %.3g" % (self.value, power))
        dot.node(t2, "(%.3g/%.3g) ⨉ (%.3g^%.3g) ⨉ %.3g" % (self.uncertainty, self.value, self.value, power, power))
        dot.edge(operator_node, t1, xlabel=' Value ')
        dot.edge(operator_node, t2, label=' Uncertainty ')
        return StdUncertaintyFull(temp, abs((self.uncertainty / abs(self.value)) * temp * power), t1, t2)

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)


def sin(o):
    value = math.sin(o.value)
    uncertainty = math.cos(o.value) * o.uncertainty
    return SimpleUncertaintyFull(value, abs(math.sin(o.value + o.uncertainty) - value),
                                 *unary_temp_node_full(o, 'sin','a','b'))


U = SimpleUncertaintyFull
sin(U(3,5))
# U(3, 5) / U(3, 5)
# print(type(U(2, 4)).__name__)
dot.save('files/file.gv')
