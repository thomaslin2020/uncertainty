from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sys
from graphviz import Digraph

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
            print(str(dot))
            try:
                return jsonify({'result': result, 'graph': str(dot)})
            except:
                return 'Please fix your equation'


if __name__ == '__main__':
    app.run(port='5000', debug=True)
