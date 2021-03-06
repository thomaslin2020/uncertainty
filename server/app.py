import math
import os
import re
import sys
from datetime import datetime
from decimal import Decimal
from locale import atof

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from graphviz import Digraph
from setuptools.namespaces import flatten

app = Flask(__name__)
app.config.from_object(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRESQL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, resources={r'/*': {'origins': '*'}})
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

constants_full = {
    "simple": {
        "pi": "SimpleUncertaintyFull(math.pi, 0, symbol='π')",
        "e": "SimpleUncertaintyFull(math.e, 0, symbol='e')",
        "tau": "SimpleUncertaintyFull(math.tau, 0, symbol='τ')"
    },
    "standard": {
        "pi": "StdUncertaintyFull(math.pi, 0, symbol='π')",
        "e": "StdUncertaintyFull(math.e, 0, symbol='e')",
        "tau": "StdUncertaintyFull(math.tau, 0, symbol='τ')"
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


class Calculation(db.Model):
    __tablename__ = 'calculation'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    equation = db.Column(db.Text)
    mode = db.Column(db.String(8))
    show_graph = db.Column(db.Boolean)
    rounding = db.Column(db.Integer)
    answer = db.Column(db.Text)
    success = db.Column(db.Boolean)
    full = db.Column(db.Boolean)

    def __init__(self, date, equation, mode, show_graph, rounding, answer, success, full):
        self.date = date
        self.equation = equation
        self.mode = mode
        self.show_graph = show_graph
        self.rounding = rounding
        self.answer = answer
        self.success = success
        self.full = full

    def __repr__(self):
        return f"<Equation {self.equation}>"


def start_session(f='pdf'):
    n = iter(range(sys.maxsize))
    d = Digraph(strict=False, format=f)
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


class SimpleUncertainty:  # normal
    def __init__(self, value, uncertainty, *nodes, last_operator=None, last_node=None, temp=None, symbol=None):
        if not isinstance(value, (int, float)):
            self.value = value.value
            remove_trace([value.node])
        else:
            self.value = value
        if not isinstance(uncertainty, (int, float)):
            self.uncertainty = uncertainty.value
            remove_trace([uncertainty.node])
        else:
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
                return SimpleUncertainty(self.value - other, self.uncertainty, operator_node,
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
        operator = '⨉'
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
        operator = '⨉'
        temp = temp_node(self, other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        operator_node = binary_node(self, temp, operator)
        return SimpleUncertainty(self.value * other, self.uncertainty * other, operator_node,
                                 last_operator=operator,
                                 last_node=operator_node, temp=None)

    def __truediv__(self, other):
        operator = '÷'
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
                    other.uncertainty / abs(other.value))) * temp),
                                     operator_node, last_operator=operator, last_node=operator_node, temp=None)

    def __rtruediv__(self, other):
        operator = '÷'
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
        if not isinstance(power, (int, float)):
            remove_trace([power.node])
            power = power.value
        operator_node = str(next(num))
        power_node = str(next(num))
        dot.node(power_node, '%.3g' % power)
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        dot.edge(power_node, operator_node)
        temp = self.value ** power
        return SimpleUncertainty(temp, abs((self.uncertainty / abs(self.value)) * temp * power), operator_node)

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)


class StdUncertainty:  # normal
    def __init__(self, value, uncertainty, *nodes, last_operator=None, last_node=None, temp=None, symbol=None):
        if not isinstance(value, (int, float)):
            self.value = value.value
            remove_trace([value.node])
        else:
            self.value = value
        if not isinstance(uncertainty, (int, float)):
            self.uncertainty = uncertainty.value
            remove_trace([uncertainty.node])
        else:
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
                return StdUncertainty(self.value - other, self.uncertainty, operator_node,
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
        operator = '⨉'
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
        operator = '⨉'
        temp = temp_node(self, other)
        dot.node(self.node, '%.3g' % other)
        dot.node(temp, '%s' % self.symbol) if self.symbol else dot.node(temp, '(%.3g±%.3g)' % (
            self.value, self.uncertainty))
        operator_node = binary_node(self, temp, operator)
        return StdUncertainty(self.value * other, self.uncertainty * other, operator_node,
                              last_operator=operator,
                              last_node=operator_node, temp=None)

    def __truediv__(self, other):
        operator = '÷'
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
                                  operator_node, last_operator=operator, last_node=operator_node, temp=None)

    def __rtruediv__(self, other):
        operator = '÷'
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
        if not isinstance(power, (int, float)):
            remove_trace([power.node])
            power = power.value
        operator_node = str(next(num))
        power_node = str(next(num))
        dot.node(power_node, '%.3g' % power)
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        dot.edge(power_node, operator_node)
        temp = self.value ** power
        return StdUncertainty(temp, abs((self.uncertainty / abs(self.value)) * temp * power), operator_node)

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)


class SimpleUncertaintyFull:  # normal
    def __init__(self, value, uncertainty, *nodes, symbol=None):
        if not isinstance(value, (int, float)):
            self.value = value.value
            remove_trace([value.node])
        else:
            self.value = value
        if not isinstance(uncertainty, (int, float)):
            self.uncertainty = uncertainty.value
            remove_trace([uncertainty.node])
        else:
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
        if not isinstance(power, (int, float)):
            remove_trace([power.node])
            power = power.value
        operator_node = str(next(num))
        power_node = str(next(num))
        dot.node(power_node, '%.3g' % power)
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        dot.edge(power_node, operator_node)
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
        if not isinstance(value, (int, float)):
            self.value = value.value
            remove_trace([value.node])
        else:
            self.value = value
        if not isinstance(uncertainty, (int, float)):
            self.uncertainty = uncertainty.value
            remove_trace([uncertainty.node])
        else:
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
        if not isinstance(power, (int, float)):
            remove_trace([power.node])
            power = power.value
        operator_node = str(next(num))
        power_node = str(next(num))
        dot.node(power_node, '%.3g' % power)
        dot.node(operator_node, operator)
        dot.edge(self.node, operator_node)
        dot.edge(power_node, operator_node)
        t1, t2 = str(next(num)), str(next(num))
        temp = self.value ** power
        dot.node(t1, "%.3g ^ %.3g" % (self.value, power))
        dot.node(t2, "(%.3g/%.3g) ⨉ (%.3g^%.3g) ⨉ %.3g" % (self.uncertainty, self.value, self.value, power, power))
        dot.edge(operator_node, t1, xlabel=' Value ')
        dot.edge(operator_node, t2, label=' Uncertainty ')
        return StdUncertaintyFull(temp, abs((self.uncertainty / abs(self.value)) * temp * power), t1, t2)

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)


class SimpleUncertaintyNoGraph:
    def __init__(self, value, uncertainty, symbol=None):
        if not isinstance(value, (int, float)):
            self.value = value.value
        else:
            self.value = value
        if not isinstance(uncertainty, (int, float)):
            self.uncertainty = uncertainty.value
        else:
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
        if not isinstance(power, (int, float)):
            power = power.value
        temp = self.value ** power
        return SimpleUncertaintyNoGraph(temp, abs((self.uncertainty / abs(self.value)) * temp * power))

    def __str__(self):
        return '(%f±%f)' % (self.value, self.uncertainty)


class StdUncertaintyNoGraph:
    def __init__(self, value, uncertainty, symbol=None):
        if not isinstance(value, (int, float)):
            self.value = value.value
        else:
            self.value = value
        if not isinstance(uncertainty, (int, float)):
            self.uncertainty = uncertainty.value
        else:
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
        if not isinstance(power, (int, float)):
            power = power.value
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
        return SimpleUncertainty(value, abs(math.sin(o.value + o.uncertainty) - value),
                                 unary_temp_node(o, 'sin'))
    elif isinstance(o, StdUncertainty):
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'sin'))
    elif isinstance(o, SimpleUncertaintyFull):
        return SimpleUncertaintyFull(value, abs(math.sin(o.value + o.uncertainty) - value),
                                     *unary_temp_node_full(o, 'sin', '%.3g' % value,
                                                           'Δ: |sin(%.3g + %.3g) - sin(%.3g)|' % (
                                                               o.value, o.uncertainty, o.value)))
    else:
        return StdUncertaintyFull(value, abs(uncertainty), *unary_temp_node_full(o, 'sin', '%.3g' % value,
                                                                                 'Δ: |cos(%.3g)⋅%.3g|' % (
                                                                                     o.value, o.uncertainty)))


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
    elif isinstance(o, StdUncertainty):
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'cos'))
    elif isinstance(o, SimpleUncertaintyFull):
        return SimpleUncertaintyFull(value, abs(math.cos(o.value + o.uncertainty) - value),
                                     *unary_temp_node_full(o, 'cos', '%.3g' % value,
                                                           'Δ: |cos(%.3g + %.3g) - cos(%.3g)|' % (
                                                               o.value, o.uncertainty, o.value)))
    else:
        return StdUncertaintyFull(value, abs(uncertainty), *unary_temp_node_full(o, 'cos', '%.3g' % value,
                                                                                 'Δ: |-sin(%.3g)⋅%.3g|' % (
                                                                                     o.value, o.uncertainty)))


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
    elif isinstance(o, StdUncertainty):
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'tan'))
    elif isinstance(o, SimpleUncertaintyFull):
        return SimpleUncertaintyFull(value, abs(math.tan(o.value + o.uncertainty) - value),
                                     *unary_temp_node_full(o, 'tan', '%.3g' % value,
                                                           'Δ: |tan(%.3g + %.3g) - tan(%.3g)|' % (
                                                               o.value, o.uncertainty, o.value)))
    else:
        return StdUncertaintyFull(value, abs(uncertainty), *unary_temp_node_full(o, 'tan', '%.3g' % value,
                                                                                 'Δ: |sec(%.3g)^2⋅%.3g|' % (
                                                                                     o.value, o.uncertainty)))


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
    elif isinstance(o, StdUncertainty):
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'arcsin'))
    elif isinstance(o, SimpleUncertaintyFull):
        return SimpleUncertaintyFull(value, abs(math.asin(o.value + o.uncertainty) - value),
                                     *unary_temp_node_full(o, 'arcsin', '%.3g' % value,
                                                           'Δ: |arcsin(%.3g + %.3g) - arcsin(%.3g)|' % (
                                                               o.value, o.uncertainty, o.value)))
    else:
        return StdUncertaintyFull(value, abs(uncertainty), *unary_temp_node_full(o, 'arcsin', '%.3g' % value,
                                                                                 'Δ: |%.3g / sqrt(1 - %.3g^2)|' % (
                                                                                     o.uncertainty, o.value)))


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
    elif isinstance(o, StdUncertainty):
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'arccos'))
    elif isinstance(o, SimpleUncertaintyFull):
        return SimpleUncertaintyFull(value, abs(math.acos(o.value + o.uncertainty) - value),
                                     *unary_temp_node_full(o, 'arccos', '%.3g' % value,
                                                           'Δ: |arccos(%.3g + %.3g) - arccos(%.3g)|' % (
                                                               o.value, o.uncertainty, o.value)))
    else:
        return StdUncertaintyFull(value, abs(uncertainty), *unary_temp_node_full(o, 'arccos', '%.3g' % value,
                                                                                 'Δ: |-%.3g / sqrt(1 - %.3g^2)|' % (
                                                                                     o.uncertainty, o.value)))


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
    elif isinstance(o, StdUncertainty):
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'arctan'))
    elif isinstance(o, SimpleUncertaintyFull):
        return SimpleUncertaintyFull(value, abs(math.atan(o.value + o.uncertainty) - value),
                                     *unary_temp_node_full(o, 'arctan', '%.3g' % value,
                                                           'Δ: |arctan(%.3g + %.3g) - arctan(%.3g)|' % (
                                                               o.value, o.uncertainty, o.value)))
    else:
        return StdUncertaintyFull(value, abs(uncertainty), *unary_temp_node_full(o, 'arctan', '%.3g' % value,
                                                                                 'Δ: |%.3g / (1 + %.3g^2)|' % (
                                                                                     o.uncertainty, o.value)))


def log(o, base=10.0):
    if isinstance(o, (int, float)):
        return math.log(o, base)
    value = math.log(o.value, base)
    uncertainty = o.uncertainty / (math.log(base, math.e) * o.value)
    base = int(base) if base == int(base) else base
    if isinstance(o, SimpleUncertaintyNoGraph):
        return SimpleUncertaintyNoGraph(value, abs(math.log(o.value + o.uncertainty, base) - value))
    elif isinstance(o, StdUncertaintyNoGraph):
        return StdUncertaintyNoGraph(value, abs(uncertainty))
    elif isinstance(o, SimpleUncertainty):
        return SimpleUncertainty(value, abs(math.log(o.value + o.uncertainty, base) - value),
                                 unary_temp_node(o, 'log%s' % base))
    elif isinstance(o, StdUncertainty):
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'log%s' % base))
    elif isinstance(o, SimpleUncertaintyFull):
        return SimpleUncertaintyFull(value, abs(math.log(o.value + o.uncertainty, base) - value),
                                     *unary_temp_node_full(o, 'log%s' % base, '%.3g' % value,
                                                           'Δ: |log%s(%.3g + %.3g) - log%s(%.3g)|' % (base,
                                                                                                      o.value,
                                                                                                      o.uncertainty,
                                                                                                      base, o.value)))
    else:
        return StdUncertaintyFull(value, abs(uncertainty), *unary_temp_node_full(o, 'log%s' % base, '%.3g' % value,
                                                                                 'Δ: |%.3g / (ln(%s)⋅%.3g)|' % (
                                                                                     o.uncertainty, base, o.value)))


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
    elif isinstance(o, StdUncertainty):
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'ln'))
    elif isinstance(o, SimpleUncertaintyFull):
        return SimpleUncertaintyFull(value, abs(math.log(o.value + o.uncertainty, math.e) - value),
                                     *unary_temp_node_full(o, 'ln', '%.3g' % value,
                                                           'Δ: |ln(%.3g + %.3g) - ln(%.3g)|' % (
                                                               o.value, o.uncertainty, o.value)))
    else:
        return StdUncertaintyFull(value, abs(uncertainty), *unary_temp_node_full(o, 'ln', '%.3g' % value,
                                                                                 'Δ: |%.3g / %.3g|' % (
                                                                                     o.uncertainty, o.value)))


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
    elif isinstance(o, StdUncertainty):
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'square'))
    elif isinstance(o, SimpleUncertaintyFull):
        return SimpleUncertaintyFull(value, abs(uncertainty),
                                     *unary_temp_node_full(o, 'square', '%.3g' % value,
                                                           'Δ: 2 ⋅ %.3g ⋅ %.3g' % (o.value, o.uncertainty)))
    else:
        return StdUncertaintyFull(value, abs(uncertainty), *unary_temp_node_full(o, 'square' % base, '%.3g' % value,
                                                                                 'Δ: 2 ⋅ %.3g ⋅ %.3g' % (
                                                                                     o.value, o.uncertainty)))


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
    elif isinstance(o, StdUncertainty):
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'square root'))
    elif isinstance(o, SimpleUncertaintyFull):
        return SimpleUncertaintyFull(value, abs(uncertainty),
                                     *unary_temp_node_full(o, 'square root', '%.3g' % value,
                                                           'Δ: %.3g / (2 ⋅ sqrt(%.3g))' % (o.uncertainty, o.value)))
    else:
        return StdUncertaintyFull(value, abs(uncertainty), *unary_temp_node_full(o, 'square root', '%.3g' % value,
                                                                                 'Δ: %.3g / (2 ⋅ sqrt(%.3g))' % (
                                                                                     o.uncertainty, o.value)))


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
    elif isinstance(o, StdUncertainty):
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'cube root'))
    elif isinstance(o, SimpleUncertaintyFull):
        return SimpleUncertaintyFull(value, abs(uncertainty),
                                     *unary_temp_node_full(o, 'cube root', '%.3g' % value,
                                                           'Δ: %.3g / (3 ⋅ (%.3g)^(2/3))' % (o.uncertainty, o.value)))
    else:
        return StdUncertaintyFull(value, abs(uncertainty), *unary_temp_node_full(o, 'cube root', '%.3g' % value,
                                                                                 'Δ: %.3g / (3 ⋅ (%.3g)^(2/3))' % (
                                                                                     o.uncertainty, o.value)))


def d2r(o):
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
    elif isinstance(o, StdUncertainty):
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'deg2rad'))
    elif isinstance(o, SimpleUncertaintyFull):
        return SimpleUncertaintyFull(value, abs(uncertainty),
                                     *unary_temp_node_full(o, 'deg2rad', '%.3g' % value,
                                                           'Δ: %.3g ⋅ π/180' % o.value))
    else:
        return StdUncertaintyFull(value, abs(uncertainty), *unary_temp_node_full(o, 'deg2rad', '%.3g' % value,
                                                                                 'Δ: %.3g ⋅ π/180' % o.uncertainty))


def r2d(o):
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
    elif isinstance(o, StdUncertainty):
        return StdUncertainty(value, abs(uncertainty), unary_temp_node(o, 'rad2deg'))
    elif isinstance(o, SimpleUncertaintyFull):
        return SimpleUncertaintyFull(value, abs(uncertainty),
                                     *unary_temp_node_full(o, 'rad2deg', '%.3g' % value,
                                                           'Δ: %.3g ⋅ 180/π' % o.value))
    else:
        return StdUncertaintyFull(value, abs(uncertainty), *unary_temp_node_full(o, 'rad2deg', '%.3g' % value,
                                                                                 'Δ: %.3g ⋅ 180/π' % o.uncertainty))


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
    o = o.replace('.', '')
    if n >= len(o) > 1:
        if o[-1] == '0':
            return o + '.'
    return o


# Note that the precision is limited by the maximum number of
# significant figures in the input
# note that the precision is limited by how python represents floats
# => numbers cannot end in a series of 0, must be followed by a non-zero number
# else 20.00 would be changed to 20.0
def round_to(o, n):
    if isinstance(o, (int, float)):
        max_sigfigs = len(atof(str(o), Decimal).as_tuple().digits)
        temp_num = np.format_float_positional(o, precision=min(max_sigfigs, n),
                                              unique=False, fractional=False, trim='k')
        temp_num = sanity_check(temp_num, min(max_sigfigs, n))
        if temp_num[-1] == '.':
            temp_num = integer_check(temp_num, min(max_sigfigs, n) + 1)
        temp_num = temp_num[:-1] if temp_num[-1] == '.' else temp_num
        return temp_num

    temp = str(o.value)
    max_sigfigs = len(atof(str(o.value), Decimal).as_tuple().digits)
    o.value = o.value if o.value < 1e-14 else o.value + 1e-15
    temp_num = np.format_float_positional(o.value, precision=min(max_sigfigs, n), unique=False, fractional=False,
                                          trim='k')
    temp_num = sanity_check(temp_num, min(max_sigfigs, n))
    temp_num = temp_num[:-1] if temp_num[-1] == '.' else temp_num
    o.uncertainty = o.uncertainty if o.uncertainty < 1e-14 else o.uncertainty + 1e-15
    uncertainty = np.format_float_positional(o.uncertainty, precision=1, unique=False, fractional=False, trim='k')
    num_type = 'float' if '.' in temp_num else 'int'
    if num_type == 'float':
        ending = temp_num[temp_num.index('.') + 1:] if '.' in temp else ''
        if set(ending) == {'0'}:  # every number after decimal point is 0
            if uncertainty[-1] != '.':
                if len(ending) < len(uncertainty[uncertainty.index('.') + 1:]):
                    return '%s ≈ (%s±%s)' % (o,
                                             temp_num[
                                             :temp_num.index('.') + len(uncertainty[uncertainty.index('.') + 1:]) + 1],
                                             '0')
            temp = uncertainty
            temp = temp[:-1] if temp[-1] == '.' else temp
            if uncertainty[-1] == '.':
                temp_num = np.format_float_positional(float(temp_num), precision=min(max_sigfigs, n),
                                                      unique=False, fractional=False, trim='k')
                temp_num = sanity_check(temp_num, min(max_sigfigs, n))
                if temp_num[-1] == '.':
                    temp_num = integer_check(temp_num, min(max_sigfigs, n) + 1)
                temp_num = temp_num[:-1] if temp_num[-1] == '.' else temp_num
                return '%s ≈ (%s±%s)' % (o, temp_num, temp)
            else:
                return '%s ≈ (%s±%s)' % (o,
                                         temp_num[
                                         :temp_num.index('.') + len(uncertainty[uncertainty.index('.') + 1:]) + 1],
                                         temp)

        # number is smaller than the smallest digit (unable to represent) - error is negligible
        elif 10 ** -(len(temp_num[temp_num.index('.'):]) - 1) > float(uncertainty):
            return '%s ≈ (%s±%s)' % (o, temp_num, '0')
        else:
            uncertainty_digits = 10 ** -math.floor(math.log10(float(uncertainty)))
            temp_num = str(round(float(temp) * uncertainty_digits) / uncertainty_digits)
            temp_num = sanity_check(temp_num, min(max_sigfigs, n))
            temp_num = temp_num[:temp_num.index('.') + 1 + len(uncertainty[uncertainty.index('.') + 1:])]
            uncertainty = uncertainty[:-1] if uncertainty[-1] == '.' else uncertainty
            if temp_num[-1] == '.':
                temp_num = integer_check(temp_num, min(max_sigfigs, n) + 1)
        return '%s ≈ (%s±%s)' % (o, temp_num, uncertainty)
    else:
        if float(uncertainty) < 0.5:
            uncertainty = '0'
            return '%s ≈ (%s±%s)' % (o, integer_check(temp_num, min(max_sigfigs, n)), uncertainty)
        else:
            uncertainty = round(float(uncertainty) if float(uncertainty) < 1e-14 else float(uncertainty) + 1e-15)
            uncertainty_digits = 10 ** math.floor(math.log10(uncertainty))
            uncertainty = '0' if uncertainty < 10 ** (len(str(temp_num)) - n) else uncertainty
            temp_num = round(round(int(temp_num) / uncertainty_digits) * uncertainty_digits)
            return '%s ≈ (%s±%s)' % (o, integer_check(str(temp_num), min(max_sigfigs, n)), uncertainty)


def r(o, n=3):  # shorthand for typing convenience
    return round_to(o, n)


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
        if request.form['showGraph'] == 'false':
            method = request.form['method']
            equation = request.form['equation'].replace('e', "eval(constants_no_graph['%s']['e'])" % method).replace(
                'tau', "eval(constants_no_graph['%s']['tau'])" % method).replace(
                'pi', "eval(constants_no_graph['%s']['pi'])" % method)

            U = SimpleUncertaintyNoGraph if request.form['method'] == 'simple' else StdUncertaintyNoGraph
            rounding_form = request.form['round']
            if rounding_form != '-1':
                rounding = 32 if rounding_form == 'max' else int(rounding_form)
            else:
                rounding = -1
            try:
                result = str(eval(equation))
                success = True
            except:
                success = False
                result = 'Please fix your equation'
            db.session.add(Calculation(date=datetime.utcnow(), equation=request.form['equation'], mode=method,
                                       show_graph=False, rounding=rounding, answer=result, success=success, full=False))
            db.session.commit()
            return jsonify({'result': result, 'graph': ''})
        else:
            num, dot = start_session()
            method = request.form['method']
            if request.form['full'] == 'false':
                U = SimpleUncertainty if method == 'simple' else StdUncertainty
                equation = request.form['equation'].replace('e', "eval(constants['%s']['e'])" % method).replace(
                    'tau', "eval(constants['%s']['tau'])" % method).replace(
                    'pi', "eval(constants['%s']['pi'])" % method)
                full = False
            else:
                U = SimpleUncertaintyFull if method == 'simple' else StdUncertaintyFull
                equation = request.form['equation'].replace('e', "eval(constants_full['%s']['e'])" % method).replace(
                    'tau', "eval(constants_full['%s']['tau'])" % method).replace(
                    'pi', "eval(constants_full['%s']['pi'])" % method)
                full = True
            rounding_form = request.form['round']
            if rounding_form != '-1':
                rounding = 32 if rounding_form == 'max' else int(rounding_form)
            else:
                rounding = -1
            try:
                result = str(eval(equation))
                graph = dot.source
                graph = graph if graph != "digraph {\n}" else ""
                if graph != '':
                    graph = "digraph {\n\t" + "bgcolor=transparent\n\t" + graph[graph.index(
                        dot.body[0].replace('\t', '').replace('\n', '')[0]):]
                success = True
            except:
                result = 'Please fix your equation'
                graph = ''
                success = False
            db.session.add(Calculation(date=datetime.utcnow(), equation=request.form['equation'], mode=method,
                                       show_graph=True, rounding=rounding, answer=result, success=success, full=full))
            db.session.commit()
            return jsonify({'result': result, 'graph': graph})


if __name__ == '__main__':
    app.run(port='5000', debug=True)
