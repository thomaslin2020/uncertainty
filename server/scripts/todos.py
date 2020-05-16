# TODO: Unit Conversion
# TODO: NLP processing
import sys
import math

# TODO: Add different levels of verbosity
# visualize uncertainty propagation

from graphviz import Digraph

from server.scripts.constants import *


def temp_node(o, name):
    node = str(next(num))
    dot.node(node, name)
    dot.edge(o.node, node)
    return node


def create_temp_node(s, o, operator):
    if not isinstance(o, (int, float)):
        o = o.node
    operator_node = str(next(num))
    dot.node(operator_node, operator)
    dot.edge(s.node, operator_node)
    dot.edge(o, operator_node)
    return operator_node


class SimpleUncertainty:  # uncertainty combined
    def __init__(self, value, uncertainty, *nodes, last_operator=None, last_node=None, in_nodes=None, temp=None):
        self.value = value
        self.uncertainty = uncertainty
        self.last_operator = last_operator
        self.last_node = last_node
        self.nodes = nodes
        self.in_nodes = in_nodes
        if temp is None:
            self.node = str(next(num))
            dot.node(self.node, '(%.3g±%.3g)' % (self.value, self.uncertainty))
            dot.edges([(n, self.node) for n in self.nodes])
        else:
            self.node = temp
            dot.node(self.node, '(%.3g±%.3g)' % (self.value, self.uncertainty))

    def __add__(self, other):
        if self.last_operator == '+' and self.last_node is not None:
            if isinstance(other, (int, float)):
                temp = str(next(num))
                dot.node(temp, str(other))
                dot.edge(temp, self.last_node)
                self.in_nodes[1] += ' + %.3g' % other
                dot.node(self.in_nodes[0], self.in_nodes[1])

                return SimpleUncertainty(self.value + other, self.uncertainty,
                                         last_operator='+',
                                         last_node=self.last_node, in_nodes=self.in_nodes,
                                         temp=str(int(self.last_node) + 3))
            elif isinstance(other, Constants):
                temp = str(next(num))
                dot.node(temp, other.symbol)
                dot.edge(temp, self.last_node)
                self.in_nodes[1] += ' + %s' % other.symbol
                dot.node(self.in_nodes[0], self.in_nodes[1])
                return SimpleUncertainty(self.value + other, self.uncertainty,
                                         last_operator='+',
                                         last_node=self.last_node, in_nodes=self.in_nodes,
                                         temp=str(int(self.last_node) + 3))
            dot.edge(other.node, self.last_node)
            self.in_nodes[1] += ' + %.3g' % other.value
            self.in_nodes[3] += ' + %.3g' % other.uncertainty
            dot.node(self.in_nodes[0], self.in_nodes[1])
            dot.node(self.in_nodes[2], self.in_nodes[3])
            return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty, last_operator='+',
                                     last_node=self.last_node, in_nodes=self.in_nodes,
                                     temp=str(int(self.last_node) + 3))
        else:
            if isinstance(other, (int, float)):
                temp = str(next(num))
                dot.node(temp, str(other))
                operator_node = str(next(num))
                dot.node(operator_node, '+')
                dot.edges([(temp, operator_node), (self.node, operator_node)])
                temp_node_1, temp_node_2 = str(next(num)), str(next(num))
                t1 = '%.3g %s %.3g' % (self.value, '+', other)
                t2 = 'Δ: %.3g' % self.uncertainty
                dot.node(temp_node_1, t1)
                dot.node(temp_node_2, t2)
                dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
                in_nodes = [temp_node_1, t1, temp_node_2, t2]
                return SimpleUncertainty(self.value + other, self.uncertainty,
                                         temp_node_1, temp_node_2, last_operator='+', last_node=operator_node,
                                         in_nodes=in_nodes, temp=None)
            elif isinstance(other, Constants):
                temp = str(next(num))
                dot.node(temp, other.symbol)
                operator_node = str(next(num))
                dot.node(operator_node, '+')
                dot.edges([(temp, operator_node), (self.node, operator_node)])
                temp_node_1, temp_node_2 = str(next(num)), str(next(num))
                t1 = '%.3g %s %s' % (self.value, '+', other.symbol)
                t2 = 'Δ: %.3g' % self.uncertainty
                dot.node(temp_node_1, t1)
                dot.node(temp_node_2, t2)
                dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
                in_nodes = [temp_node_1, t1, temp_node_2, t2]
                return SimpleUncertainty(self.value + other.value, self.uncertainty,
                                         temp_node_1,
                                         temp_node_2, last_operator='+', last_node=operator_node, in_nodes=in_nodes,
                                         temp=None)
            operator_node = str(next(num))
            dot.node(operator_node, '+')
            dot.edges([(self.node, operator_node), (other.node, operator_node)])

            temp_node_1, temp_node_2 = str(next(num)), str(next(num))
            t1 = '%.3g %s %.3g' % (self.value, '+', other.value)
            t2 = 'Δ: %.3g + %.3g' % (self.uncertainty, other.uncertainty)
            dot.node(temp_node_1, t1)
            dot.node(temp_node_2, t2)
            dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
            in_nodes = [temp_node_1, t1, temp_node_2, t2]
            return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty,
                                     temp_node_1,
                                     temp_node_2, last_operator='+', last_node=operator_node, in_nodes=in_nodes,
                                     temp=None)

    def __sub__(self, other):
        if self.last_operator == '-' and self.last_node is not None:
            if isinstance(other, (int, float)):
                temp = str(next(num))
                dot.node(temp, str(other))
                dot.edge(temp, self.last_node)
                self.in_nodes[1] += ' - %.3g' % other
                dot.node(self.in_nodes[0], self.in_nodes[1])

                return SimpleUncertainty(self.value - other, self.uncertainty,
                                         last_operator='-',
                                         last_node=self.last_node, in_nodes=self.in_nodes,
                                         temp=str(int(self.last_node) + 3))
            elif isinstance(other, Constants):
                temp = str(next(num))
                dot.node(temp, other.symbol)
                dot.edge(temp, self.last_node)
                self.in_nodes[1] += ' - %s' % other.symbol
                dot.node(self.in_nodes[0], self.in_nodes[1])
                return SimpleUncertainty(self.value + other, self.uncertainty,
                                         last_operator='-',
                                         last_node=self.last_node, in_nodes=self.in_nodes,
                                         temp=str(int(self.last_node) + 3))
            dot.edge(other.node, self.last_node)
            self.in_nodes[1] += ' - %.3g' % other.value
            self.in_nodes[3] += ' + %.3g' % other.uncertainty
            dot.node(self.in_nodes[0], self.in_nodes[1])
            dot.node(self.in_nodes[2], self.in_nodes[3])
            return SimpleUncertainty(self.value - other.value, self.uncertainty + other.uncertainty, last_operator='-',
                                     last_node=self.last_node, in_nodes=self.in_nodes,
                                     temp=str(int(self.last_node) + 3))
        else:
            if isinstance(other, (int, float)):
                temp = str(next(num))
                dot.node(temp, str(other))
                operator_node = str(next(num))
                dot.node(operator_node, '-')
                dot.edges([(temp, operator_node), (self.node, operator_node)])
                temp_node_1, temp_node_2 = str(next(num)), str(next(num))
                t1 = '%.3g %s %.3g' % (self.value, '-', other)
                t2 = 'Δ: %.3g' % self.uncertainty
                dot.node(temp_node_1, t1)
                dot.node(temp_node_2, t2)
                dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
                in_nodes = [temp_node_1, t1, temp_node_2, t2]
                return SimpleUncertainty(self.value - other, self.uncertainty,
                                         temp_node_1, temp_node_2, last_operator='-', last_node=operator_node,
                                         in_nodes=in_nodes, temp=None)
            elif isinstance(other, Constants):
                temp = str(next(num))
                dot.node(temp, other.symbol)
                operator_node = str(next(num))
                dot.node(operator_node, '-')
                dot.edges([(temp, operator_node), (self.node, operator_node)])
                temp_node_1, temp_node_2 = str(next(num)), str(next(num))
                t1 = '%.3g %s %s' % (self.value, '-', other.symbol)
                t2 = 'Δ: %.3g' % self.uncertainty
                dot.node(temp_node_1, t1)
                dot.node(temp_node_2, t2)
                dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
                in_nodes = [temp_node_1, t1, temp_node_2, t2]
                return SimpleUncertainty(self.value - other.value, self.uncertainty,
                                         temp_node_1,
                                         temp_node_2, last_operator='-', last_node=operator_node, in_nodes=in_nodes,
                                         temp=None)
            operator_node = str(next(num))
            dot.node(operator_node, '-')
            dot.edges([(self.node, operator_node), (other.node, operator_node)])

            temp_node_1, temp_node_2 = str(next(num)), str(next(num))
            t1 = '%.3g %s %.3g' % (self.value, '-', other.value)
            t2 = 'Δ: %.3g + %.3g' % (self.uncertainty, other.uncertainty)
            dot.node(temp_node_1, t1)
            dot.node(temp_node_2, t2)
            dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
            in_nodes = [temp_node_1, t1, temp_node_2, t2]
            return SimpleUncertainty(self.value - other.value, self.uncertainty + other.uncertainty,
                                     temp_node_1,
                                     temp_node_2, last_operator='-', last_node=operator_node, in_nodes=in_nodes,
                                     temp=None)

    def __mul__(self, other):
        if self.last_operator == '*' and self.last_node is not None:
            if isinstance(other, (int, float)):
                temp = str(next(num))
                dot.node(temp, str(other))
                dot.edge(temp, self.last_node)
                self.in_nodes[1] += ' ⋅ %.3g' % other
                self.in_nodes[3] += ' ⋅ %.3g' % other
                dot.node(self.in_nodes[0], self.in_nodes[1])
                dot.node(self.in_nodes[2], self.in_nodes[3])

                return SimpleUncertainty(self.value * other, self.uncertainty * other,
                                         last_operator='*',
                                         last_node=self.last_node, in_nodes=self.in_nodes,
                                         temp=str(int(self.last_node) + 3))
            elif isinstance(other, Constants):
                temp = str(next(num))
                dot.node(temp, other.symbol)
                dot.edge(temp, self.last_node)
                self.in_nodes[1] += ' ⋅ %s' % other.symbol
                dot.node(self.in_nodes[0], self.in_nodes[1])
                self.in_nodes[3] += ' ⋅ %.3g' % other.value
                dot.node(self.in_nodes[2], self.in_nodes[3])

                return SimpleUncertainty(self.value * other.value, self.uncertainty * other.value,
                                         last_operator='*',
                                         last_node=self.last_node, in_nodes=self.in_nodes,
                                         temp=str(int(self.last_node) + 3))
            dot.edge(other.node, self.last_node)
            self.in_nodes[1] += ' ⋅ %s' % other.value
            # self.in_nodes[3][3:]
            self.in_nodes[3] += ' ⋅ %.3g' % other.uncertainty  # TODO: Fix
            dot.node(self.in_nodes[0], self.in_nodes[1])
            dot.node(self.in_nodes[2], self.in_nodes[3])
            temp = self.value * other.value
            return SimpleUncertainty(temp, abs(
                ((self.uncertainty / abs(self.value)) + (other.uncertainty / abs(other.value))) * temp),
                                     last_operator='*',
                                     last_node=self.last_node, in_nodes=self.in_nodes,
                                     temp=str(int(self.last_node) + 3))
        else:
            if isinstance(other, (int, float)):
                temp = str(next(num))
                dot.node(temp, str(other))
                operator_node = str(next(num))
                dot.node(operator_node, '×')
                dot.edges([(temp, operator_node), (self.node, operator_node)])
                temp_node_1, temp_node_2 = str(next(num)), str(next(num))
                t1 = '%.3g %s %.3g' % (self.value, '⋅', other)
                t2 = 'Δ: %.3g %s %.3g' % (self.uncertainty, '⋅', other)
                dot.node(temp_node_1, t1)
                dot.node(temp_node_2, t2)
                dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
                in_nodes = [temp_node_1, t1, temp_node_2, t2]
                return SimpleUncertainty(self.value * other, self.uncertainty * other,
                                         temp_node_1, temp_node_2, last_operator='*', last_node=operator_node,
                                         in_nodes=in_nodes, temp=None)
            elif isinstance(other, Constants):
                temp = str(next(num))
                dot.node(temp, other.symbol)
                operator_node = str(next(num))
                dot.node(operator_node, '×')
                dot.edges([(temp, operator_node), (self.node, operator_node)])
                temp_node_1, temp_node_2 = str(next(num)), str(next(num))
                t1 = '%.3g %s %s' % (self.value, '⋅', other.symbol)
                t2 = 'Δ: %.3g %s %.3g' % (self.uncertainty, '⋅', other.value)
                dot.node(temp_node_1, t1)
                dot.node(temp_node_2, t2)
                dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
                in_nodes = [temp_node_1, t1, temp_node_2, t2]
                return SimpleUncertainty(self.value * other.value, self.uncertainty * other.value,
                                         temp_node_1,
                                         temp_node_2, last_operator='*', last_node=operator_node, in_nodes=in_nodes,
                                         temp=None)
            operator_node = str(next(num))
            dot.node(operator_node, '×')
            dot.edges([(self.node, operator_node), (other.node, operator_node)])

            temp_node_1, temp_node_2 = str(next(num)), str(next(num))
            t1 = '%.3g %s %.3g' % (self.value, '⋅', other.value)
            dot.node(temp_node_1, t1)
            t2 = 'Δ: (%.3g÷%.3g + %.3g÷%.3g) ⋅ %.3g' % (
                self.uncertainty, self.value, other.value, other.uncertainty, self.value * other.value)
            dot.node(temp_node_2, t2)
            dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
            in_nodes = [temp_node_1, t1, temp_node_2,
                        t2]
            temp = self.value * other.value
            return SimpleUncertainty(temp, abs(((self.uncertainty / abs(self.value)) + (
                    other.uncertainty / abs(other.value))) * temp),
                                     temp_node_1,
                                     temp_node_2, last_operator='*', last_node=operator_node, in_nodes=in_nodes,
                                     temp=None)

    def __truediv__(self, other):
        if self.last_operator == '/' and self.last_node is not None:
            if isinstance(other, (int, float)):
                temp = str(next(num))
                dot.node(temp, str(other))
                dot.edge(temp, self.last_node)
                self.in_nodes[1] += ' ÷ %.3g' % other
                self.in_nodes[3] += ' ÷ %.3g' % other
                dot.node(self.in_nodes[0], self.in_nodes[1])
                dot.node(self.in_nodes[2], self.in_nodes[3])

                return SimpleUncertainty(self.value / other, self.uncertainty / other,
                                         last_operator='/',
                                         last_node=self.last_node, in_nodes=self.in_nodes,
                                         temp=str(int(self.last_node) + 3))
            elif isinstance(other, Constants):
                temp = str(next(num))
                dot.node(temp, other.symbol)
                dot.edge(temp, self.last_node)
                self.in_nodes[1] += ' ⋅ %s' % other.symbol
                dot.node(self.in_nodes[0], self.in_nodes[1])
                self.in_nodes[3] += ' ⋅ %.3g' % other.value
                dot.node(self.in_nodes[2], self.in_nodes[3])

                return SimpleUncertainty(self.value + other, self.uncertainty,
                                         last_operator='+',
                                         last_node=self.last_node, in_nodes=self.in_nodes,
                                         temp=str(int(self.last_node) + 3))
            dot.edge(other.node, self.last_node)
            self.in_nodes[1] += ' + %s' % other.value
            self.in_nodes[3] += ' ⋅ %.3g' % other.uncertainty
            dot.node(self.in_nodes[0], self.in_nodes[1])
            dot.node(self.in_nodes[2], self.in_nodes[3])
            return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty, last_operator='+',
                                     last_node=self.last_node, in_nodes=self.in_nodes,
                                     temp=str(int(self.last_node) + 3))
        else:
            if isinstance(other, (int, float)):
                temp = str(next(num))
                dot.node(temp, str(other))
                operator_node = str(next(num))
                dot.node(operator_node, '÷')
                dot.edges([(temp, operator_node), (self.node, operator_node)])
                temp_node_1, temp_node_2 = str(next(num)), str(next(num))
                t1 = '%.3g %s %.3g' % (self.value, '÷', other)
                t2 = 'Δ: %.3g %s %.3g' % (self.uncertainty, '÷', other)
                dot.node(temp_node_1, t1)
                dot.node(temp_node_2, t2)
                dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
                in_nodes = [temp_node_1, t1, temp_node_2, t2]
                return SimpleUncertainty(self.value / other, self.uncertainty,
                                         temp_node_1, temp_node_2, last_operator='/', last_node=operator_node,
                                         in_nodes=in_nodes, temp=None)
            elif isinstance(other, Constants):
                temp = str(next(num))
                dot.node(temp, other.symbol)
                operator_node = str(next(num))
                dot.node(operator_node, '×')
                dot.edges([(temp, operator_node), (self.node, operator_node)])
                temp_node_1, temp_node_2 = str(next(num)), str(next(num))
                t1 = '%.3g %s %s' % (self.value, '⋅', other.symbol)
                t2 = 'Δ: %.3g %s %.3g' % (self.uncertainty, '⋅', other.value)
                dot.node(temp_node_1, t1)
                dot.node(temp_node_2, t2)
                dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
                in_nodes = [temp_node_1, t1, temp_node_2, t2]
                return SimpleUncertainty(self.value * other.value, self.uncertainty * other.value,
                                         temp_node_1,
                                         temp_node_2, last_operator='*', last_node=operator_node, in_nodes=in_nodes,
                                         temp=None)
            operator_node = str(next(num))
            dot.node(operator_node, '×')
            dot.edges([(self.node, operator_node), (other.node, operator_node)])

            temp_node_1, temp_node_2 = str(next(num)), str(next(num))
            t1 = '%.3g %s %.3g' % (self.value, '⋅', other.value)
            dot.node(temp_node_1, t1)
            t2 = 'Δ: (%.3g÷%.3g + %.3g÷%.3g) ⋅ %.3g' % (
                self.uncertainty, self.value, other.value, other.uncertainty, self.value * other.value)
            dot.node(temp_node_2, t2)
            dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
            in_nodes = [temp_node_1, t1, temp_node_2,
                        t2]
            temp = self.value * other.value
            return SimpleUncertainty(temp, abs(((self.uncertainty / abs(self.value)) + (
                    other.uncertainty / abs(other.value))) * temp),
                                     temp_node_1,
                                     temp_node_2, last_operator='*', last_node=operator_node, in_nodes=in_nodes,
                                     temp=None)


def start_session(verbose=2, f='pdf'):
    n = iter(range(sys.maxsize))
    d = Digraph(strict=False, comment='Computational Graph', format=f)
    return n, d, verbose


def process(string, name=None):
    print('Solution: %s' % eval(string))
    print(str(dot))
    if name:
        dot.save(name)


num, dot, level = start_session(3)
U = SimpleUncertainty
U(1, 2) * U(1, 2)
dot.save('files/file.gv')
dot.render('files/file')
