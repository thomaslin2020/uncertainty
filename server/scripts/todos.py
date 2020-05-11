# TODO: Unit Conversion
# TODO: NLP processing
import sys
import math

# TODO: Add different levels of verbosity
# group functions, self-defined functions, visualize uncertainty propagation
from contextlib import contextmanager

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


def binary_node(s, o, operator):
    global level
    operator_node = str(next(num))
    dot.node(operator_node, operator)
    dot.edges([(s.node, operator_node), (o.node, operator_node)])
    if level == 1:
        return [operator_node]
    temp_node_1 = str(next(num))
    temp_node_2 = str(next(num))
    dot.node(temp_node_1, '%.2g %s %.2g' % (s.value, operator, o.value))
    dot.node(temp_node_2, 'Δ: %.2g + %.2g' % (s.uncertainty, o.uncertainty))
    dot.edge(operator_node, temp_node_1)
    dot.edge(operator_node, temp_node_2)
    if level == 2:
        return [temp_node_1, temp_node_2]
    return [temp_node_1, temp_node_2, s.node, o.node]


def sin(o):
    value = math.sin(o.value)
    uncertainty = math.cos(o.value) * o.uncertainty
    return SimpleUncertainty(value, abs(uncertainty), temp_node(o, 'sin'))


# class SimpleUncertainty: # normal
#     def __init__(self, value, uncertainty, *nodes, last_operator=None, last_node=None, temp=None):
#         self.value = value
#         self.uncertainty = uncertainty
#         self.last_operator = last_operator
#         self.last_node = last_node
#         self.nodes = nodes
#         if temp is None:
#             self.node = str(next(num))
#             dot.node(self.node, '(%.3g±%.3g)' % (self.value, self.uncertainty))
#             dot.edges([(n, self.node) for n in self.nodes])
#         else:
#             self.node = temp
#             dot.node(self.node, '(%.3g±%.3g)' % (self.value, self.uncertainty))
#
#     def __add__(self, other):
#         if self.last_operator == '+' and self.last_node is not None and level == 0:
#             dot.edge(other.node, self.last_node)
#             return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty, last_operator='+',
#                                      last_node=self.last_node, temp=str(int(self.last_node) + 1))
#         else:
#             if level == 0:
#                 operator_node = str(next(num))
#                 dot.node(operator_node, '+')
#                 dot.edge(self.node, operator_node)
#                 dot.edge(other.node, operator_node)
#                 return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty,
#                                          operator_node, last_operator='+', last_node=operator_node, temp=None)
#             else:
#                 return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty,
#                                          *binary_node(self, other, '+'))
#
#     def __sub__(self, other):
#         if self.last_operator == '-' and self.last_node is not None and level == 0:
#             dot.edge(other.node, self.last_node)
#             return SimpleUncertainty(self.value - other.value, self.uncertainty + other.uncertainty, last_operator='-',
#                                      last_node=self.last_node, temp=str(int(self.last_node) + 1))
#         else:
#             if level == 0:
#                 operator_node = str(next(num))
#                 dot.node(operator_node, '-')
#                 dot.edge(self.node, operator_node)
#                 dot.edge(other.node, operator_node)
#                 return SimpleUncertainty(self.value - other.value, self.uncertainty + other.uncertainty,
#                                          operator_node, last_operator='-', last_node=operator_node, temp=None)
#             else:
#                 return SimpleUncertainty(self.value - other.value, self.uncertainty + other.uncertainty,
#                                          *binary_node(self, other, '-'))


class SimpleUncertainty:  # uncertainty combined

    def __init__(self, value, uncertainty, *nodes, last_operator=None, last_node=None, in_nodes=None, temp=None,
                 count=0):
        self.value = value
        self.uncertainty = uncertainty
        self.last_operator = last_operator
        self.last_node = last_node
        self.nodes = nodes
        self.count = count
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
                self.in_nodes[1] += ' + %s' % other
                dot.node(self.in_nodes[0], self.in_nodes[1])

                return SimpleUncertainty(self.value + other, self.uncertainty,
                                         last_operator='+',
                                         last_node=self.last_node, in_nodes=self.in_nodes,
                                         temp=str(int(self.last_node) + 3 + self.count), count=self.count)
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
            self.in_nodes[1] += ' + %s' % other.value
            self.in_nodes[3] += ' + %.2g' % other.uncertainty
            dot.node(self.in_nodes[0], self.in_nodes[1])
            dot.node(self.in_nodes[2], self.in_nodes[3])
            return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty, last_operator='+',
                                     last_node=self.last_node, in_nodes=self.in_nodes,
                                     temp=str(int(self.last_node) + 3), count=self.count)
        else:
            if isinstance(other, (int, float)):
                temp = str(next(num))
                dot.node(temp, str(other))
                operator_node = str(next(num))
                dot.node(operator_node, '+')
                dot.edges([(temp, operator_node), (self.node, operator_node)])
                temp_node_1, temp_node_2 = str(next(num)), str(next(num))
                dot.node(temp_node_1, '%.2g %s %.2g' % (self.value, '+', other))
                dot.node(temp_node_2, 'Δ: %.2g + %.2g' % (self.uncertainty, 0))
                dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
                in_nodes = [temp_node_1, '%.2g %s %.2g' % (self.value, '+', other), temp_node_2,
                            'Δ: %.2g + %.2g' % (self.uncertainty, 0)]
                # self.count += 1
                return SimpleUncertainty(self.value + other, self.uncertainty,
                                         temp_node_1,
                                         temp_node_2, last_operator='+', last_node=operator_node, in_nodes=in_nodes,
                                         temp=None, count=self.count)
            elif isinstance(other, Constants):
                temp = str(next(num))
                dot.node(temp, other.symbol)
                operator_node = str(next(num))
                dot.node(operator_node, '+')
                dot.edges([(temp, operator_node), (self.node, operator_node)])
                temp_node_1, temp_node_2 = str(next(num)), str(next(num))
                dot.node(temp_node_1, '%.2g %s %.2s' % (self.value, '+', other.symbol))
                dot.node(temp_node_2, 'Δ: %.2g + %.2g' % (self.uncertainty, 0))
                dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
                in_nodes = [temp_node_1, '%.2g %s %.2s' % (self.value, '+', other.symbol), temp_node_2,
                            'Δ: %.2g + %.2g' % (self.uncertainty, 0)]
                return SimpleUncertainty(self.value + other.value, self.uncertainty,
                                         temp_node_1,
                                         temp_node_2, last_operator='+', last_node=operator_node, in_nodes=in_nodes,
                                         temp=None)
            operator_node = str(next(num))
            dot.node(operator_node, '+')
            dot.edges([(self.node, operator_node), (other.node, operator_node)])

            temp_node_1, temp_node_2 = str(next(num)), str(next(num))
            dot.node(temp_node_1, '%.2g %s %.2g' % (self.value, '+', other.value))
            dot.node(temp_node_2, 'Δ: %.2g + %.2g' % (self.uncertainty, other.uncertainty))
            dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
            in_nodes = [temp_node_1, '%.2g %s %.2g' % (self.value, '+', other.value), temp_node_2,
                        'Δ: %.2g + %.2g' % (self.uncertainty, other.uncertainty)]
            return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty,
                                     temp_node_1,
                                     temp_node_2, last_operator='+', last_node=operator_node, in_nodes=in_nodes,
                                     temp=None)

    def __sub__(self, other):
        if self.last_operator == '-' and self.last_node is not None:
            dot.edge(other.node, self.last_node)

            dot.node(self.in_nodes[0], self.in_nodes[1] + ' - %s' % other.value)
            dot.node(self.in_nodes[2], self.in_nodes[3] + ' + %s' % other.uncertainty)

            return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty,
                                     last_operator='-',
                                     last_node=self.last_node, in_nodes=self.in_nodes,
                                     temp=str(int(self.last_node) + 3))
        else:
            operator_node = str(next(num))
            dot.node(operator_node, '-')
            dot.edges([(self.node, operator_node), (other.node, operator_node)])

            temp_node_1, temp_node_2 = str(next(num)), str(next(num))
            dot.node(temp_node_1, '%.2g %s %.2g' % (self.value, '-', other.value))
            dot.node(temp_node_2, 'Δ: %.2g + %.2g' % (self.uncertainty, other.uncertainty))
            dot.edges([(operator_node, temp_node_1), (operator_node, temp_node_2)])
            in_nodes = [temp_node_1, '%.2g %s %.2g' % (self.value, '-', other.value), temp_node_2,
                        'Δ: %.2g + %.2g' % (self.uncertainty, other.uncertainty)]
            return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty,
                                     temp_node_1,
                                     temp_node_2, last_operator='-', last_node=operator_node, in_nodes=in_nodes,
                                     temp=None)


# class SimpleUncertainty:  # minimal
#     def __init__(self, value, uncertainty, *nodes, last_operator=None, last_node=None, temp=None):
#         self.value = value
#         self.uncertainty = uncertainty
#         self.last_operator = last_operator
#         self.last_node = last_node
#         self.nodes = nodes
#         if temp is None:
#             self.node = str(next(num))
#             dot.node(self.node, '(%.3g±%.3g)' % (self.value, self.uncertainty))
#             for i in self.nodes:
#                 dot.edge(i, self.node, label='+')
#         else:
#             self.node = temp
#             dot.node(self.node, '(%.3g±%.3g)' % (self.value, self.uncertainty))
#
#     def __add__(self, other):
#         if self.last_operator == '+':
#             dot.edge(other.node, self.node, label='+')
#             return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty, last_operator='+',
#                                      last_node=self.last_node, temp=str(int(self.last_node) + 1))
#         else:
#             return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty,
#                                      self.node, other.node, last_operator='+',
#                                      last_node=other.node, temp=None)


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
U(1, 2) + U(3, 4) + 4 + e + U(3, 4) + pi
dot.save('files/file.gv')
dot.render('files/file')
