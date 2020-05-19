import math
import re
import sys

from graphviz import Digraph
from setuptools.namespaces import flatten


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


def remove_trace(nodes):
    o = [re.sub('\\[.*\\]', '', i).strip().replace('\t', '').replace('\n', '') for i in dot.body]
    o = [i.split(" -> ") if " -> " in i else [i] for i in o]
    temp = [(i, j) for i, j in enumerate(o) for n in nodes if n in j]
    if not temp:
        return
    index, values = list(zip(*temp))
    values = set(flatten(values))
    for i in sorted(index)[::-1]:
        dot.body.pop(i)
    for i in nodes:
        values.remove(i)
    return remove_trace(list(values))


class SimpleUncertaintyFull:  # normal
    def __init__(self, value, uncertainty, *nodes, symbol=None):
        if not isinstance(value, (int, float)):
            self.value = value.value
            remove_trace(list(value.node))
        else:
            self.value = value
        self.uncertainty = uncertainty
        self.symbol = symbol
        self.nodes = nodes
        self.node = str(next(num))
        dot.node(self.node, symbol) if symbol else dot.node(self.node,
                                                            '(%.3g±%.3g)' % (self.value, self.uncertainty))
        dot.edges([(n, self.node) for n in self.nodes])
        print(dot.source)
        if not isinstance(value, (int, float)):
            remove_trace(list(value.node))

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


def sin(o):
    if isinstance(o, (int, float)):
        return math.sin(o)
    value = math.sin(o.value)
    return SimpleUncertaintyFull(value, abs(math.sin(o.value + o.uncertainty) - value),
                                 *unary_temp_node_full(o, 'sin', '%.3g' % value,
                                                       'Δ: |sin(%.3g + %.3g) - sin(%.3g)|' % (
                                                           o.value, o.uncertainty, o.value)))


U = SimpleUncertaintyFull
sin(U(SimpleUncertaintyFull(3, 0) + 5, 5) - 2)
print(dot.source)

# U(3, 5) / U(3, 5)
# print(type(U(2, 4")).__name__)
dot.save('files/file.gv')

print("digraph {\n\tbgcolor=transparent\n\t0 [label=\"π\"]\n\t7 [label=\"(4.14±0.1)\"]\n\t8 [label=sin]\n\t7 -> 8\n\t9 [label=-0.841]\n\t10 [label=\"Δ: |sin(4.14 + 0.1) - sin(4.14)|\"]\n\t8 -> 9 [xlabel=\" Value \"]\n\t8 -> 10 [label=\" Uncertainty \"]\n\t11 [label=\"(-0.841±0.0497)\"]\n\t9 -> 11\n\t10 -> 11\n\t12 [label=\"(2±0.1)\"]\n\t13 [label=\"^\"]\n\t12 -> 13\n\t14 [label=\"2 ^ 2\"]\n\t15 [label=\"(0.1/2) ⨉ (2^2) ⨉ 2\"]\n\t13 -> 14 [xlabel=\" Value \"]\n\t13 -> 15 [label=\" Uncertainty \"]\n\t16 [label=\"(4±0.4)\"]\n\t14 -> 16\n\t15 -> 16\n\t17 [label=\"⨉\"]\n\t11 -> 17\n\t16 -> 17\n\t18 [label=\"-0.841 ⨉ 4\"]\n\t19 [label=\"Δ: [(0.0497/-0.841)+(0.4/4)] ⨉ -3.37\"]\n\t17 -> 18 [xlabel=\" Value \"]\n\t17 -> 19 [label=\" Uncertainty \"]\n\t20 [label=\"(-3.37±0.536)\"]\n\t18 -> 20\n\t19 -> 20\n\t21 [label=\"(3±0.1)\"]\n\t22 [label=\"square root\"]\n\t21 -> 22\n\t23 [label=1.73]\n\t24 [label=\"Δ: 0.1 / (2 ⋅ sqrt(3))\"]\n\t22 -> 23 [xlabel=\" Value \"]\n\t22 -> 24 [label=\" Uncertainty \"]\n\t25 [label=\"(1.73±0.0289)\"]\n\t23 -> 25\n\t24 -> 25\n\t26 [label=log10]\n\t25 -> 26\n\t27 [label=0.239]\n\t28 [label=\"Δ: |log10(1.73 + 0.0289) - log10(1.73)|\"]\n\t26 -> 27 [xlabel=\" Value \"]\n\t26 -> 28 [label=\" Uncertainty \"]\n\t29 [label=\"(0.239±0.00718)\"]\n\t27 -> 29\n\t28 -> 29\n\t30 [label=\"÷\"]\n\t20 -> 30\n\t29 -> 30\n\t31 [label=\"-3.37 / 0.239\"]\n\t32 [label=\"Δ: [(0.536/-3.37)+(0.00718/0.239)] ⨉ -14.1\"]\n\t30 -> 31 [xlabel=\" Value \"]\n\t30 -> 32 [label=\" Uncertainty \"]\n\t33 [label=\"(-14.1±2.67)\"]\n\t31 -> 33\n\t32 -> 33\n\t34 [label=\"+\"]\n\t0 -> 34\n\t33 -> 34\n\t35 [label=\"3.14 + -14.1\"]\n\t36 [label=\"Δ: 0 + 2.67\"]\n\t34 -> 35 [xlabel=\" Value \"]\n\t34 -> 36 [label=\" Uncertainty \"]\n\t37 [label=\"(-11±2.67)\"]\n\t35 -> 37\n\t36 -> 37\n}")
