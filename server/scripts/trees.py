import sys
from graphviz import Digraph

import math


def unary_temp_node(o, name):
    node = str(next(num))
    dot.node(node, name)
    dot.edge(o.node, node)
    return node


def sin(o):
    value = math.sin(o.value)
    uncertainty = math.cos(o.value) * o.uncertainty
    return SimpleUncertainty(value, abs(uncertainty), unary_temp_node(o, 'sin'))


def temp_node(s, o, last_node=False):
    temp = str(next(num))
    if isinstance(o, str):
        dot.node(temp, '%s' % o)
    else:
        dot.node(temp, '%.3g' % o)
    if last_node:
        dot.edge(temp, s.last_node)
    return temp


def binary_node(s, o, operator):
    operator_node = str(next(num))
    dot.node(operator_node, operator)
    dot.edge(s.node, operator_node)
    dot.edge(o, operator_node)
    return operator_node


class SimpleUncertainty:  # normal
    def __init__(self, value, uncertainty, *nodes, last_operator=None, last_node=None, temp=None, symbol=None):
        self.value = value
        self.uncertainty = uncertainty
        self.last_operator = last_operator
        self.last_node = last_node
        self.nodes = nodes
        self.symbol = symbol
        if temp is None:
            self.node = str(next(num))
            dot.node(self.node, symbol) if symbol else dot.node(self.node,
                                                                '(%.3g±%.3g)' % (self.value, self.uncertainty))
            dot.edges([(n, self.node) for n in self.nodes])
        else:
            self.node = temp
            dot.node(self.node, symbol) if symbol else dot.node(self.node,
                                                                '(%.3g±%.3g)' % (self.value, self.uncertainty))

    def __add__(self, other):
        operator = '+'
        if self.last_operator == operator and self.last_node is not None:
            if isinstance(other, (int, float)):
                temp_node(self, other, True)
                return SimpleUncertainty(self.value + other, self.uncertainty,
                                         last_operator=operator,
                                         last_node=self.last_node, temp=str(int(self.last_node) + 1))
            dot.edge(other.node, self.last_node)
            return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty,
                                     last_operator=operator,
                                     last_node=self.last_node, temp=str(int(self.last_node) + 1))
        else:
            if isinstance(other, (int, float)):
                temp = temp_node(self, other)
                operator_node = binary_node(self, temp, operator)
                return SimpleUncertainty(self.value + other, self.uncertainty, operator_node,
                                         last_operator=operator,
                                         last_node=operator_node, temp=None)
            operator_node = binary_node(self, other.node, operator)
            return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty,
                                     operator_node, last_operator=operator, last_node=operator_node, temp=None)

    def __radd__(self, other):
        operator = '+'
        temp = temp_node(self, other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        operator_node = binary_node(self, temp, operator)
        return SimpleUncertainty(self.value + other, self.uncertainty, operator_node,
                                 last_operator=operator,
                                 last_node=operator_node, temp=None)

    def __sub__(self, other):
        operator = '-'
        if self.last_operator == operator and self.last_node is not None:
            if isinstance(other, (int, float)):
                temp_node(self, other, True)
                return SimpleUncertainty(self.value - other, self.uncertainty,
                                         last_operator=operator,
                                         last_node=self.last_node, temp=str(int(self.last_node) + 1))
            dot.edge(other.node, self.last_node)
            return SimpleUncertainty(self.value - other.value, self.uncertainty + other.uncertainty,
                                     last_operator=operator,
                                     last_node=self.last_node, temp=str(int(self.last_node) + 1))
        else:
            if isinstance(other, (int, float)):
                temp = temp_node(self, other)
                operator_node = binary_node(self, temp, operator)
                return SimpleUncertainty(self.value + other, self.uncertainty, operator_node,
                                         last_operator=operator,
                                         last_node=operator_node, temp=None)
            operator_node = binary_node(self, other.node, operator)
            return SimpleUncertainty(self.value - other.value, self.uncertainty + other.uncertainty,
                                     operator_node, last_operator=operator, last_node=operator_node, temp=None)

    def __rsub__(self, other):
        operator = '-'
        temp = temp_node(self, other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        operator_node = binary_node(self, temp, operator)
        return SimpleUncertainty(other - self.value, self.uncertainty, operator_node,
                                 last_operator=operator,
                                 last_node=operator_node, temp=None)

    def __mul__(self, other):
        operator = '*'
        if self.last_operator == operator and self.last_node is not None:
            if isinstance(other, (int, float)):
                temp_node(self, other, True)
                return SimpleUncertainty(self.value * other, self.uncertainty * other,
                                         last_operator=operator,
                                         last_node=self.last_node, temp=str(int(self.last_node) + 1))
            dot.edge(other.node, self.last_node)
            temp = self.value * other.value
            return SimpleUncertainty(temp, abs(((self.uncertainty / abs(self.value)) + (
                    other.uncertainty / abs(other.value))) * temp), last_operator=operator,
                                     last_node=self.last_node, temp=str(int(self.last_node) + 1))
        else:
            if isinstance(other, (int, float)):
                temp = temp_node(self, other)
                operator_node = binary_node(self, temp, operator)
                return SimpleUncertainty(self.value * other, self.uncertainty * other, operator_node,
                                         last_operator=operator,
                                         last_node=operator_node, temp=None)
            operator_node = binary_node(self, other.node, operator)
            temp = self.value * other.value
            return SimpleUncertainty(temp, abs(((self.uncertainty / abs(self.value)) + (
                    other.uncertainty / abs(other.value))) * temp), self.uncertainty + other.uncertainty,
                                     operator_node, last_operator=operator, last_node=operator_node, temp=None)

    def __rmul__(self, other):
        operator = '*'
        temp = temp_node(self, other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        operator_node = binary_node(self, temp, operator)
        return SimpleUncertainty(self.value * other, self.uncertainty * other, operator_node,
                                 last_operator=operator,
                                 last_node=operator_node, temp=None)

    def __truediv__(self, other):
        operator = '/'
        if self.last_operator == operator and self.last_node is not None:
            if isinstance(other, (int, float)):
                temp_node(self, other, True)
                return SimpleUncertainty(self.value / other, self.uncertainty / other,
                                         last_operator=operator,
                                         last_node=self.last_node, temp=str(int(self.last_node) + 1))
            dot.edge(other.node, self.last_node)
            temp = self.value / other.value
            return SimpleUncertainty(temp, abs(((self.uncertainty / abs(self.value)) + (
                    other.uncertainty / abs(other.value))) * temp), last_operator=operator,
                                     last_node=self.last_node, temp=str(int(self.last_node) + 1))
        else:
            if isinstance(other, (int, float)):
                temp = temp_node(self, other)
                operator_node = binary_node(self, temp, operator)
                return SimpleUncertainty(self.value / other, self.uncertainty / other, operator_node,
                                         last_operator=operator,
                                         last_node=operator_node, temp=None)
            operator_node = binary_node(self, other.node, operator)
            temp = self.value / other.value
            return SimpleUncertainty(temp, abs(((self.uncertainty / abs(self.value)) + (
                    other.uncertainty / abs(other.value))) * temp), self.uncertainty + other.uncertainty,
                                     operator_node, last_operator=operator, last_node=operator_node, temp=None)

    def __rtruediv__(self, other):
        operator = '/'
        temp = temp_node(self, other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        operator_node = binary_node(self, temp, operator)
        temp = other / self.value
        return SimpleUncertainty(temp, temp * self.uncertainty / self.value, operator_node,
                                 last_operator=operator,
                                 last_node=operator_node, temp=None)

    def __pow__(self, power):
        operator = '^'
        operator_node = str(next(num))
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        temp = self.value ** power
        return SimpleUncertainty(temp, abs((self.uncertainty / abs(self.value)) * temp * power), operator_node)

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)


constants = {
    "pi": "SimpleUncertainty(math.pi, 0, symbol='π')",
    "e": "SimpleUncertainty(math.e, 0, symbol='e')",
    "tau": "SimpleUncertainty(math.tau, 0, symbol='τ')"
}


def start_session(f='pdf'):
    n = iter(range(sys.maxsize))
    d = Digraph(strict=False, comment='Computational Graph', format=f)
    return n, d


def process(s, name=None):
    print('Solution: %s' % eval(s))
    print(str(dot))
    if name:
        dot.save(name)


num, dot = start_session()
U = SimpleUncertainty
# U(1, 2) + 5 + U(1, 2) + e
string = "5/e"
string = string.replace('pi', "eval(constants['pi'])") \
    .replace('e', "eval(constants['e'])").replace('tau', "eval(constants['tau'])")
eval(string)
dot.save('files/file.gv')
dot.render('files/file')
