import math
import numpy as np
import sys

from decimal import Decimal
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from graphviz import Digraph
from locale import atof

app = Flask(__name__)
app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})

constants = {
    "simple": {
        "pi": "SimpleUncertainty(math.pi, 0, symbol='π')",
        "e": "SimpleUncertainty(math.e, 0, symbol='e')",
        "tau": "SimpleUncertainty(math.tau, 0, symbol='τ')"
    },
    "standard": {
        "pi": "StdUncertainty(math.pi, 0, symbol='π')",
        "e": "StdUncertainty(math.e, 0, symbol='e')",
        "tau": "StdUncertainty(math.tau, 0, symbol='τ')"
    }
}

constants_no_graph = {
    "simple": {
        "pi": "SimpleUncertaintyNoGraph(math.pi, 0, symbol='π')",
        "e": "SimpleUncertaintyNoGraph(math.e, 0, symbol='e')",
        "tau": "SimpleUncertaintyNoGraph(math.tau, 0, symbol='τ')"
    },
    "standard": {
        "pi": "StdUncertaintyNoGraph(math.pi, 0, symbol='π')",
        "e": "StdUncertaintyNoGraph(math.e, 0, symbol='e')",
        "tau": "StdUncertaintyNoGraph(math.tau, 0, symbol='τ')"
    }
}


def start_session(f='pdf'):
    n = iter(range(sys.maxsize))
    d = Digraph(strict=False, comment='Computational Graph', format=f)
    return n, d


num, dot = start_session()


def unary_temp_node(o, name):
    node = str(next(num))
    dot.node(node, name)
    dot.edge(o.node, node)
    return node


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

    def __neg__(self):
        operator = 'neg'
        operator_node = str(next(num))
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        return SimpleUncertainty(-self.value, self.uncertainty, operator_node)

    def __abs__(self):
        operator = 'abs'
        operator_node = str(next(num))
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        return SimpleUncertainty(abs(self.value), self.uncertainty, operator_node)

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
                    other.uncertainty / abs(other.value))) * temp),
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


class StdUncertainty:  # normal
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

    def __neg__(self):
        operator = 'neg'
        operator_node = str(next(num))
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        return StdUncertainty(-self.value, self.uncertainty, operator_node)

    def __abs__(self):
        operator = 'abs'
        operator_node = str(next(num))
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        return StdUncertainty(abs(self.value), self.uncertainty, operator_node)

    def __add__(self, other):
        operator = '+'
        if self.last_operator == operator and self.last_node is not None:
            if isinstance(other, (int, float)):
                temp_node(self, other, True)
                return StdUncertainty(self.value + other, self.uncertainty,
                                      last_operator=operator,
                                      last_node=self.last_node, temp=str(int(self.last_node) + 1))
            dot.edge(other.node, self.last_node)
            return StdUncertainty(self.value + other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2),
                                  last_operator=operator,
                                  last_node=self.last_node, temp=str(int(self.last_node) + 1))
        else:
            if isinstance(other, (int, float)):
                temp = temp_node(self, other)
                operator_node = binary_node(self, temp, operator)
                return StdUncertainty(self.value + other, self.uncertainty, operator_node,
                                      last_operator=operator,
                                      last_node=operator_node, temp=None)
            operator_node = binary_node(self, other.node, operator)
            return StdUncertainty(self.value + other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2),
                                  operator_node, last_operator=operator, last_node=operator_node, temp=None)

    def __radd__(self, other):
        operator = '+'
        temp = temp_node(self, other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        operator_node = binary_node(self, temp, operator)
        return StdUncertainty(self.value + other, self.uncertainty, operator_node,
                              last_operator=operator,
                              last_node=operator_node, temp=None)

    def __sub__(self, other):
        operator = '-'
        if self.last_operator == operator and self.last_node is not None:
            if isinstance(other, (int, float)):
                temp_node(self, other, True)
                return StdUncertainty(self.value - other, self.uncertainty,
                                      last_operator=operator,
                                      last_node=self.last_node, temp=str(int(self.last_node) + 1))
            dot.edge(other.node, self.last_node)
            return StdUncertainty(self.value - other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2),
                                  last_operator=operator,
                                  last_node=self.last_node, temp=str(int(self.last_node) + 1))
        else:
            if isinstance(other, (int, float)):
                temp = temp_node(self, other)
                operator_node = binary_node(self, temp, operator)
                return StdUncertainty(self.value + other, self.uncertainty, operator_node,
                                      last_operator=operator,
                                      last_node=operator_node, temp=None)
            operator_node = binary_node(self, other.node, operator)
            return StdUncertainty(self.value - other.value, math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2),
                                  operator_node, last_operator=operator, last_node=operator_node, temp=None)

    def __rsub__(self, other):
        operator = '-'
        temp = temp_node(self, other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        operator_node = binary_node(self, temp, operator)
        return StdUncertainty(other - self.value, self.uncertainty, operator_node,
                              last_operator=operator,
                              last_node=operator_node, temp=None)

    def __mul__(self, other):
        operator = '*'
        if self.last_operator == operator and self.last_node is not None:
            if isinstance(other, (int, float)):
                temp_node(self, other, True)
                return StdUncertainty(self.value * other, self.uncertainty * other,
                                      last_operator=operator,
                                      last_node=self.last_node, temp=str(int(self.last_node) + 1))
            dot.edge(other.node, self.last_node)
            temp = self.value * other.value
            return StdUncertainty(temp, abs(math.sqrt(
                ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp),
                                  last_operator=operator,
                                  last_node=self.last_node, temp=str(int(self.last_node) + 1))
        else:
            if isinstance(other, (int, float)):
                temp = temp_node(self, other)
                operator_node = binary_node(self, temp, operator)
                return StdUncertainty(self.value * other, self.uncertainty * other, operator_node,
                                      last_operator=operator,
                                      last_node=operator_node, temp=None)
            operator_node = binary_node(self, other.node, operator)
            temp = self.value * other.value
            return StdUncertainty(temp, abs(math.sqrt(
                ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp),
                                  operator_node, last_operator=operator, last_node=operator_node, temp=None)

    def __rmul__(self, other):
        operator = '*'
        temp = temp_node(self, other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        operator_node = binary_node(self, temp, operator)
        return StdUncertainty(self.value * other, self.uncertainty * other, operator_node,
                              last_operator=operator,
                              last_node=operator_node, temp=None)

    def __truediv__(self, other):
        operator = '/'
        if self.last_operator == operator and self.last_node is not None:
            if isinstance(other, (int, float)):
                temp_node(self, other, True)
                return StdUncertainty(self.value / other, self.uncertainty / other,
                                      last_operator=operator,
                                      last_node=self.last_node, temp=str(int(self.last_node) + 1))
            dot.edge(other.node, self.last_node)
            temp = self.value / other.value
            return StdUncertainty(temp, abs(math.sqrt(
                ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp),
                                  last_operator=operator,
                                  last_node=self.last_node, temp=str(int(self.last_node) + 1))
        else:
            if isinstance(other, (int, float)):
                temp = temp_node(self, other)
                operator_node = binary_node(self, temp, operator)
                return StdUncertainty(self.value / other, self.uncertainty / other, operator_node,
                                      last_operator=operator,
                                      last_node=operator_node, temp=None)
            operator_node = binary_node(self, other.node, operator)
            temp = self.value / other.value
            return StdUncertainty(temp, abs(math.sqrt(
                ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp),
                                  self.uncertainty + other.uncertainty,
                                  operator_node, last_operator=operator, last_node=operator_node, temp=None)

    def __rtruediv__(self, other):
        operator = '/'
        temp = temp_node(self, other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        operator_node = binary_node(self, temp, operator)
        temp = other / self.value
        return StdUncertainty(temp, temp * self.uncertainty / self.value, operator_node,
                              last_operator=operator,
                              last_node=operator_node, temp=None)

    def __pow__(self, power):
        operator = '^'
        operator_node = str(next(num))
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        temp = self.value ** power
        return StdUncertainty(temp, abs((self.uncertainty / abs(self.value)) * temp * power), operator_node)

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)


class SimpleUncertaintyNoGraph:
    def __init__(self, value, uncertainty, symbol=None):
        self.value = value
        self.uncertainty = uncertainty

    def __neg__(self):
        return SimpleUncertaintyNoGraph(-self.value, self.uncertainty)

    def __abs__(self):
        return SimpleUncertaintyNoGraph(abs(self.value), self.uncertainty)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertaintyNoGraph(self.value + other, self.uncertainty)
        return SimpleUncertaintyNoGraph(self.value + other.value, self.uncertainty + other.uncertainty)

    def __radd__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertaintyNoGraph(self.value + other, self.uncertainty)
        return SimpleUncertaintyNoGraph(self.value + other.value, self.uncertainty + other.uncertainty)

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertaintyNoGraph(self.value - other, self.uncertainty)
        return SimpleUncertaintyNoGraph(self.value - other.value, self.uncertainty + other.uncertainty)

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertaintyNoGraph(other - self.value, self.uncertainty)
        return SimpleUncertaintyNoGraph(other.value - self.value, self.uncertainty + other.uncertainty)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertaintyNoGraph(self.value * other, self.uncertainty * other)
        temp = self.value * other.value
        return SimpleUncertaintyNoGraph(temp,
                                        abs(((self.uncertainty / abs(self.value)) + (
                                                other.uncertainty / abs(other.value))) * temp))

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertaintyNoGraph(self.value * other, self.uncertainty * other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertaintyNoGraph(self.value / other, self.uncertainty / other)
        temp = self.value / other.value
        return SimpleUncertaintyNoGraph(temp,
                                        abs(((self.uncertainty / abs(self.value)) + (
                                                other.uncertainty / abs(other.value))) * temp))

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            return SimpleUncertaintyNoGraph(other, 0) / SimpleUncertaintyNoGraph(self.value, self.uncertainty)

    def __pow__(self, power):
        temp = self.value ** power
        return SimpleUncertaintyNoGraph(temp, abs((self.uncertainty / abs(self.value)) * temp * power))

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)


class StdUncertaintyNoGraph:
    def __init__(self, value, uncertainty, symbol=None):
        self.value = value
        self.uncertainty = uncertainty

    def __neg__(self):
        return StdUncertaintyNoGraph(-self.value, self.uncertainty)

    def __abs__(self):
        return StdUncertaintyNoGraph(abs(self.value), self.uncertainty)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertaintyNoGraph(self.value + other, self.uncertainty)
        return StdUncertaintyNoGraph(self.value + other.value,
                                     math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2))

    def __radd__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertaintyNoGraph(self.value + other, self.uncertainty)
        return StdUncertaintyNoGraph(self.value + other.value,
                                     math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2))

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertaintyNoGraph(self.value - other, self.uncertainty)
        return StdUncertaintyNoGraph(self.value - other.value,
                                     math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2))

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertaintyNoGraph(other - self.value, self.uncertainty)
        return StdUncertaintyNoGraph(self.value - other.value,
                                     math.sqrt(self.uncertainty ** 2 + other.uncertainty ** 2))

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertaintyNoGraph(self.value * other, self.uncertainty * other)
        temp = self.value * other.value
        return StdUncertaintyNoGraph(temp, abs(math.sqrt(
            ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp))

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertaintyNoGraph(self.value * other, self.uncertainty * other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertaintyNoGraph(self.value / other, self.uncertainty / other)
        temp = self.value / other.value
        return StdUncertaintyNoGraph(temp, abs(math.sqrt(
            ((self.uncertainty / abs(self.value)) ** 2) + ((other.uncertainty / abs(other.value)) ** 2)) * temp))

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            return StdUncertaintyNoGraph(other, 0) / StdUncertaintyNoGraph(self.value, self.uncertainty)

    def __pow__(self, power):
        temp = self.value ** power
        return StdUncertaintyNoGraph(temp, abs((self.uncertainty / abs(self.value)) * temp * power))

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)


def sin(o):
    if isinstance(o, (int, float)):
        return math.sin(o)
    value = math.sin(o.value)
    uncertainty = math.cos(o.value) * o.uncertainty
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(math.sin(o.value + o.uncertainty) - value))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(math.sin(o.value + o.uncertainty) - value), unary_temp_node(o, 'sin'))
    else:
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'sin'))


def cos(o):
    if isinstance(o, (int, float)):
        return math.cos(o)
    value = math.cos(o.value)
    uncertainty = math.sin(o.value) * o.uncertainty
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(math.cos(o.value + o.uncertainty) - value))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(math.cos(o.value + o.uncertainty) - value), unary_temp_node(o, 'cos'))
    else:
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'cos'))


def tan(o):
    if isinstance(o, (int, float)):
        return math.tan(o)
    value = math.tan(o.value)
    uncertainty = o.uncertainty / (math.cos(o.value) ** 2)
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(math.tan(o.value + o.uncertainty) - value))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(math.tan(o.value + o.uncertainty) - value), unary_temp_node(o, 'tan'))
    else:
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'tan'))


def asin(o):
    if isinstance(o, (int, float)):
        return math.asin(o)
    value = math.asin(o.value)
    uncertainty = o.uncertainty / math.sqrt(1 - o.value ** 2)
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(math.asin(o.value + o.uncertainty) - value))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(math.asin(o.value + o.uncertainty) - value), unary_temp_node(o, 'arcsin'))
    else:
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'arcsin'))


def acos(o):
    if isinstance(o, (int, float)):
        return math.acos(o)
    value = math.acos(o.value)
    uncertainty = -o.uncertainty / math.sqrt(1 - o.value ** 2)
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(math.acos(o.value + o.uncertainty) - value))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(math.acos(o.value + o.uncertainty) - value), unary_temp_node(o, 'arccos'))
    else:
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'arccos'))


def atan(o):
    if isinstance(o, (int, float)):
        return math.atan(o)
    value = math.atan(o.value)
    uncertainty = o.uncertainty / (1 + o.value ** 2)
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(math.atan(o.value + o.uncertainty) - value))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(math.atan(o.value + o.uncertainty) - value), unary_temp_node(o, 'arctan'))
    else:
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'arctan'))


def log(o, base=10.0):
    if isinstance(o, (int, float)):
        return math.log(o, base)
    value = math.log(o.value, base)
    uncertainty = o.uncertainty / (math.log(base, math.e) * o.value)
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(math.log(o.value + o.uncertainty, base) - value))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(math.log(o.value + o.uncertainty, base) - value),
                                 unary_temp_node(o, 'log%s' % base))
    else:
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'log%s' % base))


def ln(o):
    if isinstance(o, (int, float)):
        return math.log(o, math.e)
    value = math.log(o.value, math.e)
    uncertainty = o.uncertainty / o.value
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(math.log(o.value + o.uncertainty, math.e) - value))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(math.log(o.value + o.uncertainty, math.e) - value),
                                 unary_temp_node(o, 'ln'))
    else:
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'ln'))


def sq(o):
    if isinstance(o, (int, float)):
        return o * o
    value = o.value * o.value
    uncertainty = 2 * o.value * o.uncertainty
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(uncertainty), unary_temp_node(o, 'square'))
    else:
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'square'))


def sqrt(o):
    if isinstance(o, (int, float)):
        return math.sqrt(o)
    value = math.sqrt(o.value)
    uncertainty = 1 / (2 * math.sqrt(o.value)) * o.uncertainty
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(uncertainty), unary_temp_node(o, 'square root'))
    else:
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'square root'))


def cbrt(o):
    if isinstance(o, (int, float)):
        return math.pow(o, 1 / 3)
    value = math.pow(o.value, 1 / 3)
    uncertainty = 1 / (3 * (o.value ** (2 / 3))) * o.uncertainty
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(uncertainty), unary_temp_node(o, 'cube root'))
    else:
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'cube root'))


def deg2rad(o):
    if isinstance(o, (int, float)):
        return o * math.pi / 180
    temp = math.pi / 180
    value = o.value * temp
    uncertainty = o.uncertainty * temp
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(uncertainty), unary_temp_node(o, 'deg2rad'))
    else:
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'deg2rad'))


def rad2deg(o):
    if isinstance(o, (int, float)):
        return o * 180 / math.pi
    temp = 180 / math.pi
    value = o.value * temp
    uncertainty = o.uncertainty * temp
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(uncertainty), unary_temp_node(o, 'rad2deg'))
    else:
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'rad2deg'))


def exp(o):
    if isinstance(o, (int, float)):
        return math.exp(o)


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


# Note that the precision is limited by the maximum number of
# significant figures in the input
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
            temp_num = np.format_float_positional(o, precision=min(max_sigfigs, n),
                                                  unique=False, fractional=False, trim='k')
            temp_num = sanity_check(temp_num, min(max_sigfigs, n))
        else:
            temp_num = np.format_float_positional(o, precision=min(n, 15),
                                                  unique=False, fractional=False, trim='k')
            temp_num = sanity_check(temp_num, n)
        if temp_num[-1] == '.':
            if cap_sigfigs:
                temp_num = integer_check(temp_num, min(max_sigfigs, n) + 1)
            else:
                temp_num = integer_check(temp_num, min(n, 15) + 1)
        temp_num = temp_num[:-1] if temp_num[-1] == '.' else temp_num
        return temp_num

    temp = str(o.value)
    max_sigfigs = 0
    if cap_sigfigs:
        max_sigfigs = len(atof(str(o.value), Decimal).as_tuple().digits)
        o.value = o.value if o.value < 1e-14 else o.value + 1e-15
        temp_num = np.format_float_positional(o.value, precision=min(max_sigfigs, n), unique=False, fractional=False,
                                              trim='k')
        temp_num = sanity_check(temp_num, min(max_sigfigs, n))
    else:
        o.value = o.value if o.value < 1e-14 else o.value + 1e-15
        temp_num = np.format_float_positional(o.value, precision=min(n, 15), unique=False, fractional=False,
                                              trim='k')
        temp_num = sanity_check(temp_num, min(n, 15))
    temp_num = temp_num[:-1] if temp_num[-1] == '.' else temp_num
    o.uncertainty = o.uncertainty if o.uncertainty < 1e-14 else o.uncertainty + 1e-15
    uncertainty = np.format_float_positional(o.uncertainty, precision=1, unique=False, fractional=False, trim='k')
    num_type = 'float' if '.' in temp_num else 'int'
    if num_type == 'float':
        ending = temp_num[temp_num.index('.') + 1:] if '.' in temp else ''
        if set(ending) == {'0'}:  # every number after decimal point is 0
            if uncertainty[-1] != '.':
                if len(ending) < len(uncertainty[uncertainty.index('.') + 1:]):
                    return '(%s±%s)' % (
                        temp_num[:temp_num.index('.') + len(uncertainty[uncertainty.index('.') + 1:]) + 1], '0')
            temp = uncertainty
            temp = temp[:-1] if temp[-1] == '.' else temp
            if uncertainty[-1] == '.':
                if cap_sigfigs:
                    temp_num = np.format_float_positional(float(temp_num), precision=min(max_sigfigs, n),
                                                          unique=False, fractional=False, trim='k')
                    temp_num = sanity_check(temp_num, min(max_sigfigs, n))
                else:
                    temp_num = np.format_float_positional(float(temp_num), precision=min(n, 15),
                                                          unique=False, fractional=False, trim='k')
                    temp_num = sanity_check(temp_num, min(n, 15))
                if temp_num[-1] == '.':
                    if cap_sigfigs:
                        temp_num = integer_check(temp_num, min(max_sigfigs, n) + 1)
                    else:
                        temp_num = integer_check(temp_num, min(n, 15) + 1)
                temp_num = temp_num[:-1] if temp_num[-1] == '.' else temp_num
                return '(%s±%s)' % (temp_num, temp)
            else:
                return '(%s±%s)' % (
                    temp_num[:temp_num.index('.') + len(uncertainty[uncertainty.index('.') + 1:]) + 1], temp)

        # number is smaller than the smallest digit (unable to represent) - error is negligible
        elif 10 ** -(len(temp_num[temp_num.index('.'):]) - 1) > float(uncertainty):
            return '(%s±%s)' % (temp_num, '0')
        else:
            uncertainty_digits = 10 ** -math.floor(math.log10(float(uncertainty)))
            temp_num = str(round(float(temp) * uncertainty_digits) / uncertainty_digits)
            if cap_sigfigs:
                temp_num = sanity_check(temp_num, min(max_sigfigs, n))
                temp_num = temp_num[:temp_num.index('.') + 1 + len(uncertainty[uncertainty.index('.') + 1:])]
            else:
                temp_num = np.format_float_positional(o.value, precision=min(n, 15),
                                                      unique=False, fractional=False, trim='k')
                temp_num = sanity_check(temp_num, min(n, 15))
            uncertainty = uncertainty[:-1] if uncertainty[-1] == '.' else uncertainty
            if temp_num[-1] == '.':
                if cap_sigfigs:
                    temp_num = integer_check(temp_num, min(max_sigfigs, n) + 1)
                else:
                    temp_num = integer_check(temp_num, min(n, 15) + 1)
        return '(%s±%s)' % (temp_num, uncertainty)
    else:
        if float(uncertainty) < 0.5:
            uncertainty = '0'
            if cap_sigfigs:
                return '(%s±%s)' % (integer_check(temp_num, min(max_sigfigs, n)), uncertainty)
            else:
                return '(%s±%s)' % (integer_check(temp_num, min(n, 15)), uncertainty)
        else:
            uncertainty = round(float(uncertainty) if float(uncertainty) < 1e-14 else float(uncertainty) + 1e-15)
            uncertainty_digits = 10 ** math.floor(math.log10(uncertainty))
            uncertainty = '0' if uncertainty < 10 ** (len(str(temp_num)) - n) else uncertainty
            temp_num = round(round(int(temp_num) / uncertainty_digits) * uncertainty_digits)
            if cap_sigfigs:
                return '(%s±%s)' % (integer_check(str(temp_num), min(max_sigfigs, n)), uncertainty)
            else:
                return '(%s±%s)' % (integer_check(str(temp_num), min(n, 15)), uncertainty)


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
# print(r_(SimpleUncertainty(1.2345678, 5), 90))

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World'


@app.route('/api/calculate', methods=['POST'])
def calculate():
    global num, dot
    if request.method == 'POST':
        U = None
        if request.form['showGraph'] == 'false':
            method = request.form['method']
            equation = request.form['equation'].replace('pi', "eval(constants_no_graph['%s']['pi'])" % method) \
                .replace('e', "eval(constants_no_graph['%s']['e'])" % method).replace('tau',
                                                                                      "eval(constants_no_graph['%s']['tau'])" % method)
            U = SimpleUncertaintyNoGraph if request.form['method'] == 'simple' else StdUncertaintyNoGraph
            try:
                return str(eval(equation))
            except:
                return 'Please fix your equation'
        else:
            num, dot = start_session()
            method = request.form['method']
            U = SimpleUncertainty if method == 'simple' else StdUncertainty
            equation = request.form['equation'].replace('pi', "eval(constants['%s']['pi'])" % method) \
                .replace('e', "eval(constants['%s']['e'])" % method).replace('tau', "eval(constants['%s']['tau'])" %
                                                                             method)
            result = str(eval(equation))
            try:
                graph = str(dot)
                graph = graph if graph != "// Computational Graph\ndigraph {\n}" else ""
                return jsonify({'result': result, 'graph': graph})
            except:
                return 'Please fix your equation'


if __name__ == '__main__':
    app.run(port='5000', debug=True)
